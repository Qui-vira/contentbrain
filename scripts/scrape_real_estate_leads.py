"""
Altara Aerial — Real Estate Agent Finder
Scrapes Nigeria Property Centre, PropertyPro, and Jiji for property listings
in Lagos, Abuja, and Port Harcourt that have no aerial photos.
Extracts agent name, phone, listing URL. Saves to Supabase and CSV.

Usage:
    python scripts/scrape_real_estate_leads.py                # All cities
    python scripts/scrape_real_estate_leads.py --city Lagos    # Single city
    python scripts/scrape_real_estate_leads.py --dry-run       # Scrape only, no Supabase
"""

import os
import sys
import re
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from altara_lead_base import (
    run_apify_actor, save_csv, upsert_leads, promote_to_mql,
    log_scan, ensure_dirs, CITIES
)
from altara_telegram import notify_scan_complete

# --- Scraping configs ---

PROPERTY_SITES = [
    {
        'name': 'Nigeria Property Centre',
        'slug': 'npc',
        'base_urls': {
            'Lagos': 'https://nigeriapropertycentre.com/for-sale/houses/lagos/showtype',
            'Abuja': 'https://nigeriapropertycentre.com/for-sale/houses/abuja/showtype',
            'Port Harcourt': 'https://nigeriapropertycentre.com/for-sale/houses/rivers/showtype',
        },
    },
    {
        'name': 'PropertyPro',
        'slug': 'propertypro',
        'base_urls': {
            'Lagos': 'https://www.propertypro.ng/property-for-sale/in/lagos',
            'Abuja': 'https://www.propertypro.ng/property-for-sale/in/abuja',
            'Port Harcourt': 'https://www.propertypro.ng/property-for-sale/in/rivers',
        },
    },
    {
        'name': 'Jiji',
        'slug': 'jiji',
        'base_urls': {
            'Lagos': 'https://jiji.ng/lagos/houses-apartments-for-sale',
            'Abuja': 'https://jiji.ng/abuja/houses-apartments-for-sale',
            'Port Harcourt': 'https://jiji.ng/rivers/houses-apartments-for-sale',
        },
    },
]

AERIAL_KEYWORDS = [
    'aerial', 'drone', 'bird eye', 'bird\'s eye', 'sky view',
    'overhead', 'top view', 'elevated view', 'above',
]


def scrape_property_site(site, city):
    """Scrape a property listing site for listings in a given city."""
    url = site['base_urls'].get(city)
    if not url:
        return []

    label = f"{site['slug']}-{city}"
    print(f'\n  Scraping {site["name"]} — {city}...')

    # Use Apify cheerio-scraper to extract listing data
    results = run_apify_actor('apify~cheerio-scraper', {
        'startUrls': [{'url': url}],
        'maxRequestsPerCrawl': 50,
        'pageFunction': """
async function pageFunction(context) {
    const { $, request } = context;
    const listings = [];

    // Generic selectors that work across property sites
    const listingSelectors = [
        '.property-list .single-room-sale',   // NPC
        '.single-room-sale',                   // NPC alt
        '.listings-property',                  // PropertyPro
        '.b-list-advert__item-wrapper',        // Jiji
        '.qa-advert-list-item',                // Jiji alt
        '[data-testid="listing-card"]',        // generic
        '.property-item',                      // generic
        '.listing-item',                       // generic
    ];

    let $listings = $([]);
    for (const sel of listingSelectors) {
        $listings = $(sel);
        if ($listings.length > 0) break;
    }

    $listings.each((i, el) => {
        const $el = $(el);

        // Extract listing URL
        const linkEl = $el.find('a[href*="property"], a[href*="listing"], a[href*="houses"], a.item-title, h3 a, h4 a').first();
        let listingUrl = linkEl.attr('href') || '';
        if (listingUrl && !listingUrl.startsWith('http')) {
            listingUrl = new URL(listingUrl, request.url).href;
        }

        // Extract title
        const title = linkEl.text().trim() || $el.find('h3, h4, .title, .property-title').first().text().trim();

        // Extract price
        const price = $el.find('.price, .amount, [class*="price"]').first().text().trim();

        // Extract agent/seller info
        const agent = $el.find('.marketed-by, .agent-name, .seller-name, [class*="agent"], [class*="seller"]').first().text().trim();

        // Extract phone (often hidden, but sometimes visible)
        const phoneEl = $el.find('a[href^="tel:"], [class*="phone"], [class*="tel"]').first();
        const phone = phoneEl.attr('href')?.replace('tel:', '') || phoneEl.text().trim();

        // Check images for aerial keywords
        const images = [];
        $el.find('img').each((j, img) => {
            const alt = $(img).attr('alt') || '';
            const src = $(img).attr('src') || $(img).attr('data-src') || '';
            images.push({ alt, src });
        });

        const imageCount = images.length;
        const hasAerial = images.some(img =>
            ['aerial', 'drone', 'bird', 'sky view', 'overhead', 'above'].some(kw =>
                img.alt.toLowerCase().includes(kw)
            )
        );

        if (title || listingUrl) {
            listings.push({
                title: title.substring(0, 200),
                listing_url: listingUrl,
                price,
                agent_name: agent,
                phone,
                image_count: imageCount,
                has_aerial: hasAerial,
                source: request.url,
            });
        }
    });

    return listings;
}
""",
    }, label=label, timeout_mins=5)

    return results


def extract_leads_from_listings(listings, city, source_site):
    """Filter listings without aerial photos and extract agent leads."""
    leads = []
    seen_phones = set()

    for listing in listings:
        # Skip listings that already have aerial photos
        if listing.get('has_aerial', False):
            continue

        phone = listing.get('phone', '').strip()
        agent = listing.get('agent_name', '').strip()
        listing_url = listing.get('listing_url', '')

        # Need at least a phone or agent name
        if not phone and not agent:
            continue

        # Dedup on phone
        if phone and phone in seen_phones:
            continue
        if phone:
            seen_phones.add(phone)

        # Score the lead
        score = score_real_estate_lead(listing, city)

        leads.append({
            'name': agent,
            'company': '',
            'phone': phone,
            'email': '',
            'website': '',
            'address': '',
            'city': city,
            'listing_url': listing_url,
            'instagram': '',
            'followers': 0,
            'score': score,
            'lifecycle_stage': 'subscriber',
            'source': f'{source_site} scrape',
            'notes': f"Listing: {listing.get('title', '')[:100]}. "
                     f"Images: {listing.get('image_count', 0)}. No aerial photos.",
        })

    return leads


def score_real_estate_lead(listing, city):
    """Score a real estate lead 0-10 based on quality signals."""
    score = 0

    # Has phone number (essential for outreach)
    if listing.get('phone'):
        score += 3

    # Has agent name
    if listing.get('agent_name'):
        score += 1

    # High image count but no aerial = they care about photos but missing drone
    img_count = listing.get('image_count', 0)
    if img_count >= 5:
        score += 2
    elif img_count >= 3:
        score += 1

    # Premium listing signals (price text suggests high-value property)
    price_text = listing.get('price', '').lower()
    if any(x in price_text for x in ['million', 'm', '100', '200', '300', '500']):
        score += 2

    # Lagos premium areas
    title = (listing.get('title', '') or '').lower()
    premium_areas = ['lekki', 'ikoyi', 'vi', 'banana island', 'maitama', 'asokoro', 'gwarinpa', 'wuse', 'garki']
    if any(area in title for area in premium_areas):
        score += 1

    # Has listing URL (can reference in outreach)
    if listing.get('listing_url'):
        score += 1

    return min(round(score, 1), 10)


CSV_FIELDS = [
    'name', 'phone', 'city', 'listing_url', 'score',
    'lifecycle_stage', 'source', 'notes',
]


def main():
    parser = argparse.ArgumentParser(description='Altara Aerial — Real Estate Agent Finder')
    parser.add_argument('--city', choices=CITIES, help='Scrape single city')
    parser.add_argument('--dry-run', action='store_true', help='Skip Supabase, CSV only')
    args = parser.parse_args()

    cities = [args.city] if args.city else CITIES
    ensure_dirs()

    print('=' * 50)
    print('  ALTARA AERIAL — Real Estate Lead Finder')
    print(f'  Cities: {", ".join(cities)}')
    print('=' * 50)

    all_leads = []
    errors = []

    for site in PROPERTY_SITES:
        for city in cities:
            try:
                listings = scrape_property_site(site, city)
                leads = extract_leads_from_listings(listings, city, site['name'])
                all_leads.extend(leads)
                print(f'  {site["name"]} / {city}: {len(leads)} leads (no aerial photos)')
            except Exception as e:
                errors.append(f'{site["slug"]}/{city}: {e}')
                print(f'  ERROR: {site["slug"]}/{city}: {e}')

    # Dedup across all sites by phone
    deduped = {}
    for lead in all_leads:
        key = lead.get('phone') or lead.get('name', '') + lead.get('city', '')
        if key and key not in deduped:
            deduped[key] = lead
        elif key and lead['score'] > deduped[key]['score']:
            deduped[key] = lead

    final_leads = sorted(deduped.values(), key=lambda x: x['score'], reverse=True)
    print(f'\n  Total unique leads: {len(final_leads)}')

    # Save CSV
    date_str = datetime.now().strftime('%Y-%m-%d')
    save_csv(final_leads, f'real-estate-leads-{date_str}.csv', CSV_FIELDS)

    # Save to Supabase
    saved = 0
    promoted = 0
    if not args.dry_run:
        saved = upsert_leads(final_leads, 'real_estate')
        promoted = promote_to_mql('real_estate')
        print(f'  Supabase: {saved} saved, {promoted} promoted to MQL')

    # Log
    error_str = '; '.join(errors) if errors else None
    log_scan('real_estate_finder', len(final_leads), saved, promoted, error_str)

    # Telegram notification
    notify_scan_complete('Real Estate Finder', len(final_leads), saved, promoted, error_str)

    print(f'\n{"=" * 50}')
    print(f'  COMPLETE — {len(final_leads)} leads found')
    print(f'  Top 5:')
    for lead in final_leads[:5]:
        print(f'    {lead["name"] or "Unknown"} | {lead["phone"]} | {lead["city"]} | Score: {lead["score"]}')
    print(f'{"=" * 50}')


if __name__ == '__main__':
    main()
