# Altara Aerial by Big Quiv — Product Requirements Document (PRD)

**Version:** 1.0
**Date:** 2026-04-05
**Author:** Damilare David K. (Big Quiv)
**Status:** Draft — Pending Approval

---

## 1. App Overview

**App Name:** Altara Aerial by Big Quiv
**Tagline:** "We deliver professional drone footage without the hassle of owning, flying, or managing a drone."
**What It Is:** A two-sided marketplace that connects drone camera operators (pilots) with clients who need aerial photography and videography. Think inDrive/Bolt but for drone camera gigs.
**Location:** Lagos, Nigeria (expandable)
**Currency:** Nigerian Naira (₦)
**GitHub Repo:** `altara-aerial`

### Mission
To provide reliable, professional aerial documentation that captures ambition, progress, and moments that matter — helping clients tell their stories clearly and confidently from above.

### Vision
To become the most trusted aerial storytelling partner in Lagos, known for professionalism, planning, and perspective in a fast-moving city where details and timing make the difference.

### Core Values
- Professionalism
- Reliability
- Perspective
- Planning & Precision
- Story Driven Work

### Target Clients
- Real estate developers
- Construction companies
- Event planners
- Corporate brands
- Storytellers and creators

---

## 2. Brand Assets

| Asset | Value |
|-------|-------|
| **Logo** | Arrow/mountain mark (gradient light blue → cyan) + "ALTARA AERIAL by Big Quiv" wordmark |
| **Primary Color (Dark Blue)** | `#052237` |
| **Secondary Color (Sky Blue)** | `#399DE3` |
| **Accent Color (Cyan)** | `#86E5ED` |
| **Primary Font** | Nasalization (headings, logo text) |
| **Secondary Font** | Neue Montreal (body text, UI elements) |
| **Logo Variations** | Dark bg: white logo. Light bg: blue gradient logo. Gradient bg: white logo. |
| **Logo Rules** | No squeezing, no off-brand colors, no off-brand fonts, no rearranging, no stretching, no stroking |

**Brand Guideline Source:** `ALTARA BRAND GUIDELINE.pdf` (19-page visual identity document)

---

## 3. User Roles

### 3.1 Client
- Books drone pilots for aerial photography/videography gigs
- Posts jobs, reviews offers, selects pilots, pays via escrow, receives deliverables
- Can save favorite pilots and rebook with discount
- Business account option available (for agencies)

### 3.2 Pilot
- Drone camera operator who accepts gigs
- Browses job feed (map + list), makes offers/counteroffers
- Uploads deliverables after completing gigs
- Gets paid via instant bank transfer after delivery confirmed

### 3.3 Admin
- Platform operator (in-app admin section, not separate panel)
- Manages pilot verification, disputes, commissions, user accounts, chat flags
- Configures platform settings (commission rate, cancellation fee, min gig price)

### 3.4 Role Rules
- **No role switching.** Each account is either Client or Pilot. Must create a separate account for the other role.
- Admin role is assigned manually at database level.

---

## 4. Auth Flow

- **Method:** Phone number OTP only. No email auth.
- **Provider:** Termii (Nigerian SMS provider, ~₦2-4/SMS)
- **Auth Backend:** Supabase Auth
- **Flow:**
  1. User enters phone number
  2. Termii sends 6-digit OTP via SMS
  3. User enters OTP
  4. If new user: role selection screen (Client or Pilot)
  5. Profile setup form based on role
  6. Account created

### Signup Fields

**Client:**
- Display name
- Phone (auth only, never exposed)
- Location (city)
- Profile photo (optional)
- Company name (optional)

**Pilot:**
- Display name
- Phone (auth only, never exposed)
- Location (city)
- Profile photo
- Drone model
- NCAA RPAS certificate (upload)
- Portfolio (minimum 3 photos/videos)

---

## 5. Core Flow (inDrive Model)

### Step-by-Step

1. **Client posts a job**
   - Service type (photography, videography, real estate, wedding, construction, event, etc.)
   - Location (pin on map or typed address)
   - Date and time
   - Budget (₦)
   - Description
   - Reference photos (optional)

2. **Nearby pilots see the job**
   - Job appears in pilot's feed (map view with pins + scrollable list view, toggleable)
   - Shows: client display name, city/area, service type, budget, date
   - NO exact address shown (city + area only)

3. **Pilots respond**
   - Accept the client's price
   - Make a counteroffer (max 2 counteroffers per pilot per job)
   - Skip

4. **Client reviews offers**
   - Sees all pilot offers with: price, rating, portfolio preview, distance from job, equipment list
   - Can view full pilot profile

5. **Client selects a pilot**
   - Picks preferred pilot from offer list

6. **Both confirm — Gig is booked**
   - Client pays immediately (funds held in escrow)
   - After escrow is funded: pilot sees full job address, masked calling enabled

7. **Gig day — Pilot checks in**
   - GPS-verified arrival at location
   - Live tracking visible to client during gig

8. **Pilot completes work**
   - Uploads deliverables (photos/videos) to Supabase Storage via app

9. **Client reviews deliverables**
   - Confirms delivery is satisfactory
   - OR requests revision (pilot re-uploads)

10. **Payment released**
    - Escrow releases funds to pilot's bank account (instant transfer)
    - Platform commission (10%, configurable) deducted automatically

11. **Both rate each other**
    - 5-star rating + optional written review
    - Two-way: client rates pilot AND pilot rates client
    - Ratings are public

### Job Expiry
- Jobs auto-expire after 48 hours if no pilot offer is accepted

### Cancellation Policy
- Client cancels within 24 hours of gig: loses 10% of gig price (paid to pilot)
- Cancellation fee percentage configurable in admin
- Client cancels more than 24 hours before gig: full refund

---

## 6. Privacy & Contact Protection System

This is the most critical system in the app. It prevents disintermediation and protects user privacy.

### Rule 1: Phone Number is Auth Only

Phone number is used for OTP login via Termii. That is its ONLY purpose. It is NEVER displayed anywhere in the app to any other user.

- Store phone number in `auth.users` table only (Supabase managed)
- The `public.profiles` table must NOT contain a phone number column
- Every user gets a UUID as their public account ID
- UUID appears in URLs, booking references, chat threads, and API responses. Never the phone number.

**`auth.users` table (Supabase managed):**
- `id` (UUID, primary key)
- `phone` (used for OTP login only, never exposed via API)

**`public.profiles` table:**
- `id` (UUID, references auth.users.id)
- `display_name` (text)
- `role` (enum: client, pilot, admin)
- `avatar_url` (text, Supabase Storage)
- `location_city` (text)
- `created_at` (timestamp)
- NO phone column
- NO email column
- NO whatsapp column

### Rule 2: What Each Side Sees

**Client sees about a Pilot:**
- Display name, profile photo
- Location (city level only, e.g., "Lagos" not "123 Admiralty Way, Lekki")
- Rating (stars + review count), completed gigs count
- Services offered, equipment list (drone model, camera specs)
- Portfolio (photos/videos)
- NCAA verified badge (yes/no)
- Member since date, response time (average)
- Distance from job location (km)
- NO phone, email, WhatsApp, or home address

**Pilot sees about a Client:**
- Display name, profile photo
- Location (city level only)
- Rating (stars + review count), total gigs booked
- Member since date
- NO phone, email, WhatsApp, or address (job location shared only after booking confirmed + escrow funded)

### Rule 3: Communication Flow

**Before booking (negotiation phase):**
- In-app chat ONLY between client and pilot
- Chat is tied to the specific job post (not a general DM)
- NO phone numbers visible, NO ability to share contact info
- Chat monitoring active

**After booking confirmed AND escrow funded:**
- In-app chat continues
- Masked calling enabled (Termii voice API)
  - Client taps "Call Pilot" button
  - App routes call through masked number
  - Neither side sees the other's real phone number
  - Call logged in booking record
- Full job address now visible to pilot

**After gig completed and payment released:**
- Contact info remains shared (they already have it from the gig)
- Future bookings must go through app for escrow protection
- Rebooking prompt: "Book [pilot name] again? Get 5% off through the app."

### Rule 4: Job Location Privacy

- During negotiation (before booking): pilots see CITY and APPROXIMATE AREA only (e.g., "Lekki, Lagos" or "Wuse, Abuja"). NOT the exact address.
- After booking confirmed + escrow funded: pilot sees FULL ADDRESS and can navigate via maps.

### Rule 5: Chat Monitoring (Anti-Disintermediation)

**Flagged patterns:**

Phone number patterns:
- 11 consecutive digits (Nigerian mobile: 08012345678)
- Digits with spaces/dashes (080 1234 5678, 080-1234-5678)
- +234 prefix variations
- Any string of 7+ digits in a row

Contact sharing keywords:
- "whatsapp", "whatsapp me", "call me on", "my number is", "text me"
- "reach me at", "contact me", "send me your number", "here is my number"
- "DM me on", "instagram", "IG:", "telegram"
- "@" followed by text (social media handles)
- "gmail", "yahoo", "hotmail", "email"

**Behavior when flagged:**
- DO NOT block the message (blocking feels aggressive)
- Deliver the message normally
- Show soft warning banner to BOTH users: "Reminder: Booking through the app protects both sides with escrow and insurance. Off-platform transactions are not covered."
- Log flagged message in admin dashboard (booking ID, user ID, message text, timestamp, flag reason)

**Edge cases:**
- Do not flag "4K resolution" or similar non-phone numbers
- Do not flag prices ("150000" followed by "naira", "NGN", or "k")
- Use regex for 7+ consecutive digits, then exclude price patterns

### Rule 6: API Security

- No API endpoint returns a user's phone number to another user
- `GET /pilots/{id}`: returns display_name, avatar, location_city, rating, gigs_count, portfolio, equipment, services, ncaa_verified, member_since. NO phone.
- `GET /clients/{id}`: returns display_name, avatar, location_city, rating, gigs_booked, member_since. NO phone.
- `GET /bookings/{id}`: returns job location ONLY if requesting user is the booked pilot AND escrow is funded. Otherwise city-level only.
- `GET /me/profile`: only endpoint that returns phone (user viewing their own profile)
- Admin endpoints can access phone numbers for dispute resolution only

### Rule 7: Database Row Level Security (Supabase RLS)

```sql
-- Booking location: pilot sees full address only after escrow funded
CREATE POLICY "pilot_sees_full_location" ON public.bookings
FOR SELECT USING (
  pilot_id = auth.uid()
  AND escrow_status = 'funded'
);

-- Before escrow: pilot sees city-level location only via jobs table
CREATE POLICY "pilot_sees_job_area" ON public.jobs
FOR SELECT USING (
  status = 'open' OR status = 'negotiating'
);
-- jobs.city (text), jobs.area (text) = always visible
-- jobs.full_address (text) = only visible via booking after escrow

-- Chat messages: only visible to participants
CREATE POLICY "chat_participants_only" ON public.messages
FOR SELECT USING (
  sender_id = auth.uid() OR receiver_id = auth.uid()
);
```

### Rule 8: UI Display Patterns

**Pilot card (in job offer list):**
```
[Avatar] John D.          ★ 4.8 (23 gigs)
         Lagos, 12km away
         DJI Mavic 3 Pro | 4K Video
         ✓ NCAA Verified
         Offer: ₦180,000
         [View Portfolio] [Accept] [Counter]
```
NO phone. NO email. NO WhatsApp icon.

**Client card (in pilot's job feed):**
```
[Avatar] Adebayo O.       ★ 4.5 (8 bookings)
         Lekki, Lagos
         Needs: Real Estate Aerial Video
         Budget: ₦150,000
         Date: April 15, 2026
         [View Details] [Make Offer]
```
NO phone. NO email. NO address (just area).

**After booking confirmed + escrow funded:**
```
[Avatar] John D.          ★ 4.8
         [💬 Chat] [📞 Call Pilot]  ← masked call
         Job Location: 15 Admiralty Way, Lekki  ← now visible
         Date: April 15, 2026 at 10:00 AM
```

---

## 7. Payments

### Payment Methods (Client pays)
1. **Card** — Paystack or Flutterwave
2. **Bank Transfer** — Korapay
3. **USSD** — Flutterwave
4. **Crypto** — Blockradar

Client chooses payment method at checkout.

### Escrow
- Client pays on booking confirmation
- Funds held in platform escrow account
- Released to pilot after client confirms delivery
- If dispute: admin mediates

### Commission
- 10% from pilot earnings (configurable in admin)
- No service fee charged to client

### Pilot Payouts
- Instant bank transfer to pilot's registered bank account
- Triggered automatically after client confirms delivery
- Commission deducted before payout

### Minimum Gig Price
- ₦25,000

### Cancellation Fee
- Client cancels within 24 hours of gig: 10% of gig price goes to pilot
- Percentage configurable in admin

---

## 8. Features List

### V1 (Build Now)

| # | Feature | Priority |
|---|---------|----------|
| 1 | Phone OTP auth (Termii + Supabase Auth) | Critical |
| 2 | Client profiles (name, photo, location, company optional) | Critical |
| 3 | Pilot profiles (name, photo, location, equipment, NCAA cert, portfolio) | Critical |
| 4 | Job posting (service type, location, date, budget, description, ref photos) | Critical |
| 5 | Pilot job feed — map view (Google Maps pins) | Critical |
| 6 | Pilot job feed — list view (scrollable, filterable) | Critical |
| 7 | Accept/counteroffer flow (2 counters per pilot, 48hr job expiry) | Critical |
| 8 | Client offer comparison (price, rating, portfolio, distance, equipment) | Critical |
| 9 | Client selects pilot → booking confirmed | Critical |
| 10 | Booking status flow (pending → confirmed → in-progress → completed → cancelled) | Critical |
| 11 | Payments: Paystack, Flutterwave, Korapay, Blockradar | Critical |
| 12 | Escrow (hold → release on delivery confirmation) | Critical |
| 13 | Pilot uploads deliverables (photos/videos to Supabase Storage) | Critical |
| 14 | Client reviews deliverables (confirm or request revision) | Critical |
| 15 | Instant bank transfer payout to pilot (minus commission) | Critical |
| 16 | In-app chat (Supabase Realtime, tied to job post) | Critical |
| 17 | Chat monitoring — flag phone/email/WhatsApp with soft warning | High |
| 18 | Rating system — 5-star + written reviews, two-way, public | High |
| 19 | Low rating policy — warning at 3.5, auto-hide below 3.0 | High |
| 20 | Live GPS tracking during gig (client sees pilot on-site) | High |
| 21 | Nearby pilots map for clients (before posting job) | High |
| 22 | Privacy system — phone never exposed, UUID identity, city-level location | Critical |
| 23 | Masked calling after escrow funded (Termii voice) | High |
| 24 | Delayed contact info (phone hidden until escrow funded) | Critical |
| 25 | Favorite pilots (save for quick rebooking) | Medium |
| 26 | Business accounts (agencies booking multiple gigs) | Medium |
| 27 | Rebooking discount (5% off when rebooking same pilot) | Medium |
| 28 | Job location privacy (area only before escrow, full address after) | Critical |
| 29 | Admin panel — in-app (stats, pilot verification, disputes, chat flags, settings) | High |
| 30 | Push notifications (all events) | High |
| 31 | Cancellation fee (10% within 24hrs, configurable) | High |
| 32 | Transaction history (both sides) | High |
| 33 | PWA (Progressive Web App, installable) | Critical |

### V2 (Build Later)

| # | Feature |
|---|---------|
| 1 | Pro/Featured pilot tier (paid, boosted visibility) |
| 2 | Pilot availability calendar |
| 3 | React Native mobile app (iOS + Android) |
| 4 | Advanced analytics dashboard |
| 5 | Dispute mediation flow (structured) |
| 6 | Multi-language support |

---

## 9. Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js (React) on Vercel |
| **Backend** | FastAPI (Python) on Railway |
| **Database** | Supabase PostgreSQL |
| **Auth** | Supabase Auth + Termii phone OTP |
| **Storage** | Supabase Storage (portfolios, deliverables, avatars) |
| **Real-time** | Supabase Realtime (chat, notifications, live tracking) |
| **Maps** | Google Maps (geocoding, map display, distance calc, navigation) |
| **Payments** | Paystack (cards), Flutterwave (cards + USSD), Korapay (bank transfer), Blockradar (crypto) |
| **SMS** | Termii (OTP, masked calling) |
| **Push Notifications** | Web Push API (PWA) |
| **App Type** | PWA (V1), React Native (V2) |
| **Repo** | `altara-aerial` |

---

## 10. Database Schema (Outline)

### Tables

**profiles**
- id (UUID, FK → auth.users.id)
- display_name, role (client/pilot/admin), avatar_url
- location_city, bio, company_name
- created_at, updated_at

**pilot_details**
- id (UUID, FK → profiles.id)
- drone_model, camera_specs, services (text[])
- ncaa_cert_url, ncaa_verified (boolean)
- rating_avg, gigs_completed, response_time_avg
- is_active, is_hidden (auto-hide for low rating)

**client_details**
- id (UUID, FK → profiles.id)
- is_business_account (boolean)
- gigs_booked, rating_avg

**portfolio_items**
- id, pilot_id (FK → profiles.id)
- media_url, media_type (photo/video)
- title, description, created_at

**jobs**
- id, client_id (FK → profiles.id)
- service_type, description, reference_photos (text[])
- city, area, full_address (hidden until escrow)
- lat, lng
- budget, date, time
- status (open/negotiating/booked/in_progress/completed/cancelled/expired)
- expires_at (48hr from creation)
- created_at

**offers**
- id, job_id (FK → jobs.id), pilot_id (FK → profiles.id)
- price, counter_count (max 2)
- status (pending/accepted/rejected/expired)
- created_at

**bookings**
- id, job_id, client_id, pilot_id
- agreed_price, escrow_status (pending/funded/released/refunded)
- booking_status (confirmed/in_progress/completed/cancelled/disputed)
- pilot_checked_in (boolean), checked_in_at
- deliverables_uploaded (boolean)
- client_confirmed_delivery (boolean)
- cancellation_fee_applied (boolean)
- payment_method, payment_reference
- created_at

**messages**
- id, booking_id (or job_id for pre-booking chat)
- sender_id, receiver_id
- content, is_flagged (boolean), flag_reason
- created_at

**reviews**
- id, booking_id, reviewer_id, reviewee_id
- rating (1-5), comment
- created_at

**transactions**
- id, booking_id, payer_id, payee_id
- amount, commission_amount, net_amount
- payment_method, payment_reference
- type (escrow_hold/escrow_release/cancellation_fee/payout)
- status (pending/completed/failed)
- created_at

**favorites**
- id, client_id, pilot_id, created_at

**flagged_messages**
- id, message_id, booking_id, user_id
- message_text, flag_reason, reviewed_by_admin (boolean)
- created_at

**admin_settings**
- key, value (commission_rate, cancellation_fee_percent, min_gig_price, etc.)

**notifications**
- id, user_id, type, title, body
- data (jsonb), read (boolean)
- created_at

---

## 11. API Endpoints (Outline)

### Auth
- `POST /auth/send-otp` — Send OTP via Termii
- `POST /auth/verify-otp` — Verify OTP, return JWT
- `POST /auth/register` — Complete registration (role + profile)

### Profiles
- `GET /me/profile` — Own profile (includes phone)
- `PUT /me/profile` — Update own profile
- `GET /pilots/{id}` — Public pilot profile (NO phone)
- `GET /clients/{id}` — Public client profile (NO phone)
- `GET /pilots/nearby` — Pilots near a location (for client map)

### Jobs
- `POST /jobs` — Create job (client only)
- `GET /jobs` — List jobs (pilot feed, with filters: service_type, distance, budget range)
- `GET /jobs/{id}` — Job detail (city/area only, full_address hidden until escrow)
- `PUT /jobs/{id}` — Update job (client only, before booking)
- `DELETE /jobs/{id}` — Cancel job (client only, before any accepted offer)

### Offers
- `POST /jobs/{id}/offers` — Make offer (pilot)
- `PUT /offers/{id}` — Counteroffer (pilot, max 2)
- `POST /offers/{id}/accept` — Accept offer (client)
- `POST /offers/{id}/reject` — Reject offer (client)

### Bookings
- `GET /bookings` — List bookings (own)
- `GET /bookings/{id}` — Booking detail (location gated by escrow status)
- `POST /bookings/{id}/checkin` — Pilot GPS check-in
- `POST /bookings/{id}/upload` — Upload deliverables
- `POST /bookings/{id}/confirm-delivery` — Client confirms delivery
- `POST /bookings/{id}/request-revision` — Client requests revision
- `POST /bookings/{id}/cancel` — Cancel booking (applies fee if <24hrs)
- `GET /bookings/{id}/tracking` — Live GPS location (client views pilot)

### Payments
- `POST /payments/initiate` — Start payment (returns gateway URL)
- `POST /payments/webhook` — Payment gateway callback
- `POST /payments/release/{booking_id}` — Release escrow to pilot
- `GET /transactions` — Transaction history

### Chat
- `GET /messages/{job_id}` — Get messages for a job/booking
- `POST /messages` — Send message (runs through chat monitor)
- Supabase Realtime subscription for live updates

### Reviews
- `POST /bookings/{id}/review` — Submit review (post-gig)
- `GET /pilots/{id}/reviews` — Pilot reviews
- `GET /clients/{id}/reviews` — Client reviews

### Favorites
- `POST /favorites/{pilot_id}` — Add favorite
- `DELETE /favorites/{pilot_id}` — Remove favorite
- `GET /favorites` — List favorites

### Admin
- `GET /admin/dashboard` — Stats (bookings, revenue, users)
- `GET /admin/verifications` — Pending pilot verifications
- `PUT /admin/verifications/{id}` — Approve/reject pilot
- `GET /admin/flagged-messages` — Flagged chat messages
- `GET /admin/disputes` — Dispute queue
- `PUT /admin/settings` — Update platform settings
- `PUT /admin/users/{id}` — Ban/suspend/verify user

### Notifications
- `GET /notifications` — List notifications
- `PUT /notifications/{id}/read` — Mark as read

---

## 12. Wireframe Descriptions (Text-Based)

### Screen 1: Splash / Landing
- Altara Aerial logo (gradient mark + wordmark) centered
- Dark blue background (#052237)
- Tagline below logo
- "Get Started" button (Sky Blue #399DE3)

### Screen 2: Phone Number Entry
- "Enter your phone number" heading (Nasalization font)
- Nigerian flag + +234 prefix
- Phone number input field
- "Send OTP" button
- Clean white background, minimal

### Screen 3: OTP Verification
- "Enter the code sent to +234..."
- 6-digit code input (individual boxes)
- "Verify" button
- "Resend code" link with countdown timer

### Screen 4: Role Selection
- "How will you use Altara Aerial?"
- Two large cards:
  - Client card: drone icon, "I need aerial footage", brief description
  - Pilot card: controller icon, "I fly drones for hire", brief description
- Tapping a card proceeds to profile setup

### Screen 5: Profile Setup (Client)
- Display name input
- Profile photo upload (camera icon)
- Location (city) dropdown or autocomplete
- Company name (optional)
- "Complete Setup" button

### Screen 6: Profile Setup (Pilot)
- Display name input
- Profile photo upload
- Location (city)
- Drone model input
- Camera specs input
- NCAA RPAS certificate upload
- Portfolio upload (min 3 items, drag-and-drop grid)
- "Complete Setup" button

### Screen 7: Client Home
- Top: search bar + location
- Map showing nearby available pilots (pins with avatars)
- "Post a Job" floating action button (prominent, Sky Blue)
- Bottom nav: Home | My Jobs | Messages | Profile

### Screen 8: Post a Job (Client)
- Service type selector (photography, videography, real estate, wedding, construction, event, other)
- Location picker (Google Maps pin drop + address input)
- Date picker + time picker
- Budget input (₦)
- Description text area
- Reference photos upload (optional)
- "Post Job" button

### Screen 9: Pilot Home — List View
- Toggle: List | Map (top tabs)
- Scrollable job cards:
  - Client avatar + name + rating
  - Area, City (e.g., "Lekki, Lagos")
  - Service type badge
  - Budget: ₦XXX,XXX
  - Date
  - "View Details" button
- Filter bar: service type, distance, budget range
- Bottom nav: Jobs | My Gigs | Messages | Profile

### Screen 10: Pilot Home — Map View
- Full-screen Google Map with job pins
- Tapping pin shows job preview card (slides up from bottom)
- Same filter bar as list view

### Screen 11: Job Detail (Pilot View)
- Client card (avatar, name, rating, city — NO phone/address)
- Service type, description, reference photos
- Budget
- Date and time
- Location: area only (e.g., "Lekki, Lagos")
- "Accept Price" button (green)
- "Make Counter Offer" button (outline)
- "Skip" text link

### Screen 12: Counter Offer (Pilot)
- Shows client's budget
- Pilot enters their price
- Optional message to client
- "Submit Offer" button
- Shows: "Counter 1 of 2 remaining"

### Screen 13: View Offers (Client)
- Job summary at top
- List of pilot offer cards:
  - Pilot avatar, name, rating, gigs count
  - Distance from job
  - Equipment (drone model)
  - NCAA verified badge
  - Offered price
  - "View Portfolio" link
  - "Accept" button (green)
  - "Counter" button (outline)
- Sorted by: price (low to high), rating (high to low), distance (closest)

### Screen 14: Booking Confirmed
- Checkmark animation
- "Booking Confirmed!"
- Pilot info card (name, photo, rating)
- Job details (service, date, location — NOW showing full address)
- "Chat with Pilot" button
- "Call Pilot" button (masked)
- Payment receipt summary

### Screen 15: Active Gig (Client View)
- Map showing pilot's live location (blue dot)
- Pilot info card
- Job details
- Status: "Pilot on the way" → "Pilot on site" → "Gig in progress"
- "Chat" and "Call" buttons

### Screen 16: Upload Deliverables (Pilot)
- Booking summary
- File upload area (drag and drop, or camera roll)
- Supports photos and videos
- "Submit Deliverables" button
- Progress bar for upload

### Screen 17: Review Deliverables (Client)
- Photo/video gallery viewer
- "Confirm Delivery" button (green) — releases payment
- "Request Revision" button (orange) — sends back to pilot with notes

### Screen 18: Rate & Review
- "How was your experience?"
- 5-star rating (tap to select)
- Written review text area (optional)
- "Submit Review" button

### Screen 19: Messages
- List of chat threads (grouped by job)
- Each thread shows: other user's avatar, name, last message preview, timestamp
- Unread badge

### Screen 20: Chat Thread
- Standard chat UI (bubbles, timestamps)
- Soft warning banner if flagged message detected
- "Call" button in header (masked, only after escrow)
- Job/booking reference at top

### Screen 21: Profile (Own)
- Avatar, display name, role badge
- Location
- For pilots: rating, gigs completed, equipment, portfolio grid
- For clients: rating, gigs booked, favorites list
- "Edit Profile" button
- "Transaction History" link
- "Settings" (notifications)
- "Log Out"

### Screen 22: Admin Panel
- Dashboard tab: cards showing total bookings, revenue, active pilots, active clients
- Verifications tab: list of pending NCAA cert reviews (approve/reject)
- Disputes tab: dispute queue with booking details
- Flagged Messages tab: flagged chat messages with context
- Users tab: search users, view details, ban/suspend/verify
- Settings tab: commission rate, cancellation fee %, min gig price inputs

---

## 13. Build Phases

### Phase 1: Foundation (Week 1)
1. Project structure: FastAPI backend + Next.js frontend
2. Apply brand assets globally (colors, fonts, logo from brand guideline)
3. Supabase project setup (tables, auth, storage buckets, RLS policies)
4. Database schema creation (all tables from Section 10)
5. Auth flow (phone OTP via Termii, role selection, profile setup)
6. Basic API endpoints (register, login, profile CRUD)

### Phase 2: Core Flow (Week 2)
7. Client: post a job (form with all fields, Google Maps location picker)
8. Pilot: job feed (list view + map view, toggleable, filterable)
9. Pilot: accept/counter-offer flow
10. Client: view offers from multiple pilots
11. Client: select pilot, confirm booking
12. Booking status flow (pending → confirmed → in-progress → completed → cancelled)

### Phase 3: Payments & Delivery (Week 3)
13. Payment integration (Paystack, Flutterwave, Korapay, Blockradar)
14. Escrow logic (hold on booking, release on delivery confirmation)
15. Pilot: upload deliverables to Supabase Storage
16. Client: review deliverables, confirm or request revision
17. Payment release to pilot (instant bank transfer, minus commission)
18. Transaction history for both sides

### Phase 4: Chat, Ratings & Polish (Week 4)
19. In-app chat (Supabase Realtime, message table)
20. Chat monitoring (regex + keyword detection, soft warnings, admin log)
21. Masked calling (Termii voice API, post-escrow only)
22. Rating system (post-gig, two-way, 5-star + written reviews)
23. Live GPS tracking during gig
24. Nearby pilots map for clients
25. Favorite pilots
26. Business accounts
27. Rebooking discount (5%)
28. Push notifications (all events via Web Push API)
29. Admin panel (in-app: dashboard, verifications, disputes, flags, users, settings)
30. PWA setup (manifest, service worker, installable)

---

## 14. Anti-Disintermediation Summary

All V1:
1. **Delayed contact info** — Phone numbers hidden until booking confirmed + escrow funded
2. **Chat monitoring** — Flag phone/email/WhatsApp sharing with soft warning
3. **Rebooking discount** — 5% off when rebooking same pilot through app
4. **Escrow payment** — Strongest retention tool. Money is locked before contact is shared.
5. **Masked calling** — Call without revealing real phone numbers
6. **Job location privacy** — Area only until escrow funded

---

## 15. Key Business Rules

1. Minimum gig price: ₦25,000
2. Platform commission: 10% from pilot (configurable)
3. No client service fee
4. Job expires after 48 hours with no accepted offer
5. Max 2 counteroffers per pilot per job
6. Cancellation within 24hrs: client pays 10% to pilot (configurable)
7. Pilots below 3.0 rating: warning at 3.5, auto-hide below 3.0
8. Pilot NCAA cert must be verified by admin before pilot can accept gigs
9. No role switching — separate accounts for client vs pilot
10. All payments go through escrow — no direct pilot payment
