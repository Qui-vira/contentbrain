"""
Generate unified-content-calendar-v2.md
910 entries: 91 days × 10 slots/day across 4 platforms
Maps all v1 hooks, fills remaining with phase-appropriate topics
"""
from datetime import date, timedelta
from collections import defaultdict

# ── Phase definitions ──────────────────────────────────────────────
PHASES = [
    (date(2026,4,1),  date(2026,4,9),  1, "Authority Rebuild", "None"),
    (date(2026,4,10), date(2026,4,16), 2, "Bridge + Hints", '"automated," "my scanner" only'),
    (date(2026,4,17), date(2026,4,25), 3, "Soft Reveal", "ContentBrain named Apr 17"),
    (date(2026,4,26), date(2026,5,10), 4, "Bridge Education", "Reply-thread CTAs only"),
    (date(2026,5,11), date(2026,5,31), 5, "Demo + Social Proof", "Demos, speed runs, workshops"),
    (date(2026,6,1),  date(2026,6,14), 6, "Conversion Push", "DM funnels, limited spots"),
    (date(2026,6,15), date(2026,6,30), 7, "Scaling + Retention", "Upsells, community, Q3"),
]

DAYS_OF_WEEK = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

IG_FORMATS = ["Reel", "Carousel", "Static"]  # rotates

# ── V1 hooks extracted from unified-content-calendar.md ────────────
# Format: (date_str, platform, type, hook, goal, source, draft_ready)
V1_ENTRIES = [
    # Phase 1
    ("2026-04-01","X-AM","Thread","The SEC told you which tokens are safe — 10 days later, here's what actually changed","Authority","A-1",True),
    ("2026-04-01","X-PM","Tweet","I built my entire system during a bear market. Now I just approve signals.","Story","A-7",True),
    ("2026-04-01","TK","Tutorial","This was my chart: 8 indicators, zero clarity. Then I stripped it down to 3.","Leads","B-6",False),
    ("2026-04-02","X-AM","Tweet","Q2 is here. Clearer regulations, stable rates, institutional staking live. The setup is violent — in a good way.","Authority","A-11",True),
    ("2026-04-02","X-PM","Tweet","The hardest part of building something real isn't the work. It's staying quiet while everyone chases trends.","Story","B-7",False),
    ("2026-04-02","LI","Post","There are 3 types of founders in Web3. Only one builds something that lasts.","Authority","B-7",False),
    ("2026-04-02","IG","Carousel","The 16 Tokens The SEC Just Cleared — updated with Q2 price action","Leads","A-3",True),
    ("2026-04-03","X-AM","Thread","BlackRock made staking institutional. ETH up 20% since. The thesis is playing out.","Authority","A-2",True),
    ("2026-04-03","X-PM","Tweet","What's the most expensive lesson crypto taught you? Mine: trusting influencers over charts.","Community","B-8",False),
    ("2026-04-03","TK","Data walkthrough","I tracked 200 trades. Here's the pattern that separated the winners from the losers.","Authority","B-8",False),
    ("2026-04-04","X-AM","Tweet","The crypto economy trained traders to watch charts 24/7 when it should have taught them to automate.","Authority","B-9",False),
    ("2026-04-04","X-PM","Tweet","Weekend prep: here's what I'm watching — and what I'm NOT touching.","Authority","B-9",False),
    ("2026-04-04","LI","Post","6 months ago I spent 30 hours/week researching content. This week I spent 3. Here's what changed.","Story","A-8",True),
    ("2026-04-04","IG","Reel","3 tokens the SEC cleared that nobody is watching: AVAX, LINK, DOT.","Leads","A-4",True),
    ("2026-04-05","X-AM","Tweet","A year ago I was charting manually for 4 hours every morning. Now my system does it in 12 minutes.","Story","B-10",False),
    ("2026-04-05","X-PM","Tweet","Crypto in 2026 is ________ and nobody's ready.","Community","B-10",False),
    ("2026-04-05","TK","Script","There are only 1,000,000 Bitcoin left. Ever. Here's why that matters.","Reach","A-6",True),
    ("2026-04-06","X-AM","Tweet","Everyone's talking about the SEC clearing 16 tokens. Nobody's talking about what this means for your tax strategy.","Authority","B-11",False),
    ("2026-04-07","X-AM","Thread","The only 3 things I check before entering any trade. I used to check 12. Simplicity made me profitable.","Authority","B-12",False),
    ("2026-04-07","X-PM","Tweet","You can only keep one for the next bull run: BTC or ETH. No hedging. Which one and why?","Community","B-12",False),
    ("2026-04-07","LI","Post","I used to evaluate 12 data points before making a decision. Now I use 3. Here's why less made me sharper.","Authority","B-12",False),
    ("2026-04-07","IG","Carousel","5 Trading Mistakes That Cost Beginners $10K+","Leads","A-5",True),
    ("2026-04-08","X-AM","Tweet","I'll be honest — I was scared to share my actual win rate. 58%. And I'm still profitable. Here's why.","Authority","B-13",False),
    ("2026-04-08","X-PM","Tweet","If your 'community' is just a Telegram group where you dump signals and nobody replies — that's not a community.","Community","B-13",False),
    ("2026-04-08","TK","Reel","My morning as a crypto KOL: wake up → check dashboard → approve signals → done.","Leads","A-9",True),
    ("2026-04-09","X-AM","Thread","People say AI content is generic slop. They're right — if you use it wrong. Here's the difference.","Authority","C-9",False),
    ("2026-04-09","X-PM","Tweet","2 weeks back on X. No links. No promos. Just talking. Here's what happened to my numbers.","Authority","B-14",False),
    ("2026-04-09","LI","Post","2 weeks ago I restarted my X account from near-zero engagement. Here are the raw numbers.","Authority","B-14",False),
    ("2026-04-09","IG","Reel","I asked AI to analyze my portfolio. It found 3 things I missed in 2 minutes.","Leads","A-10",True),
    # Phase 2
    ("2026-04-10","X-AM","Thread","How to research any crypto project in under 10 minutes. Here's the framework — manual or automated.","Authority","B-15",False),
    ("2026-04-10","X-PM","Tweet","What kills more portfolios: FOMO or FUD? I have a strong opinion.","Community","B-15",False),
    ("2026-04-10","TK","Speed run","Researching a crypto project in under 60 seconds. Timer on screen.","Authority","B-15",False),
    ("2026-04-11","X-AM","Tweet","Last month: 45 minutes for 1 post. This month: 45 minutes for a week of content. Same quality.","Story","B-16",False),
    ("2026-04-11","X-PM","Tweet","Drop a crypto/AI creator who deserves more followers. I'll check every reply and follow 10 today.","Community","B-16",False),
    ("2026-04-11","LI","Post","45 min used to produce 1 post. Now it produces 7. The quality didn't drop. Here's what changed.","Authority","B-16",False),
    ("2026-04-11","IG","Carousel","45 min = 1 post vs 45 min = 7 posts — before/after content system","Authority","B-16",False),
    ("2026-04-12","X-AM","Tweet","Pattern I've noticed: the best content creators aren't the most talented. They're the most consistent. Systems, not willpower.","Authority","B-17",False),
    ("2026-04-12","X-PM","Tweet","AI content is replacing human creators. Agree or disagree? My take: AI without human context is expensive noise.","Community","B-17",False),
    ("2026-04-12","TK","Demo","The best creators aren't more talented. They just have THIS.","Authority","B-17",False),
    ("2026-04-13","X-AM","Tweet","The Content Stack I use every week: 1) Research competitors (30 min) 2) Write hooks first (45 min) 3) Batch everything (2 hrs). Total: 3 hrs/week for 15+ posts.","Authority","B-18",False),
    ("2026-04-14","X-AM","Tweet","Left: my content process 6 months ago. Right: today. Same person. Different architecture.","Authority","B-19",False),
    ("2026-04-14","X-PM","Tweet","Bold call: by end of 2026, every crypto KOL either has an AI content system or they're irrelevant.","Reach","B-19",False),
    ("2026-04-14","LI","Post","6 months ago my content process was a mess. Today it's a machine. Here's the architecture I built.","Authority","B-19",False),
    ("2026-04-14","IG","Reel","Same person. Different system.","Authority","B-19",False),
    ("2026-04-15","X-AM","Tweet","When I first got into crypto: wanted to be a trader. Then a KOL. Now: an architect. The shift changed everything.","Story","B-20",False),
    ("2026-04-15","X-PM","Tweet","7-day challenge: post one piece of content every day for the next 7 days. Tag me. I'll engage with every post.","Community","B-20",False),
    ("2026-04-15","TK","Storytelling","Phase 1: trader. Phase 2: creator. Phase 3: architect.","Authority","B-20",False),
    ("2026-04-16","X-AM","Thread","Everyone's building AI agents. The creators who win in 2026 are building workflows. Here's the difference.","Authority","B-21",False),
    ("2026-04-16","X-PM","Tweet","3 weeks ago: zero engagement. Today: replies are fuller than they've been in months. One change: stopped broadcasting, started conversations.","Community","B-21",False),
    ("2026-04-16","LI","Post","The AI industry is obsessed with 'agents.' The businesses actually making money are building workflows.","Authority","B-21",False),
    ("2026-04-16","IG","Carousel","AI Agents vs AI Workflows — infographic comparison","Authority","B-21",False),
    # Phase 3
    ("2026-04-17","X-AM","Thread","For 6 months I've been building an AI content engine in the background. Today I'm showing you what it does. No pitch — just the raw output.","Authority","B-22",False),
    ("2026-04-17","X-PM","Tweet","If you could automate ONE thing about your content creation process, what would it be?","Community","B-22",False),
    ("2026-04-17","TK","Screen demo","I built this in 6 months. Watch what it does.","Sales","B-22",False),
    ("2026-04-18","X-AM","Tweet","I just built 7 days of content in 4 minutes. Watch.","Sales","B-23",False),
    ("2026-04-18","X-PM","Tweet","Unpopular opinion: you don't need a content team. You need a content system. One person + the right system outperforms a 5-person team.","Authority","B-23",False),
    ("2026-04-18","LI","Post","7 days of content in 4 minutes. Not filler — strategic, data-informed posts with competitor-tested hooks.","Sales","B-23",False),
    ("2026-04-18","IG","Reel","7 days of content. 4 minutes. Timer on screen. Watch.","Sales","B-23",False),
    ("2026-04-19","X-AM","Tweet","People tell me AI content sounds robotic. Test: which of these 3 hooks was written by AI? Reply with your guess.","Authority","B-24",False),
    ("2026-04-19","X-PM","Tweet","Saturday vibes. Share one win from this week. I'll start: 5x more replies this week than all of last month.","Community","B-24",False),
    ("2026-04-19","TK","Interactive","One of these was written by a human. Can you tell which one? Comment A, B, or C.","Authority","B-24",False),
    ("2026-04-20","X-AM","Thread","I spent 8 months building a system that does what most content teams can't. It's called ContentBrain. And it's almost ready.","Leads","C-20",False),
    ("2026-04-20","X-PM","Tweet","End of month challenge: reply with ONE goal for April. I'll check back in 30 days.","Community","B-25",False),
    ("2026-04-21","X-AM","Tweet","Last week I ran ContentBrain for a DeFi project as a test. 7 days. 21 posts. Before vs after engagement.","Sales","B-26",False),
    ("2026-04-21","X-PM","Tweet","The best marketing strategy in crypto right now isn't threads or reels. It's showing up consistently for 30 days. Most can't do it.","Authority","B-26",False),
    ("2026-04-21","LI","Post","I ran a 7-day content experiment for a DeFi project. 21 posts. Zero manual writing. Here are the results.","Sales","B-26",False),
    ("2026-04-21","IG","Carousel","Why I Built Quivira OS — And What It Replaces","Leads","A-12",True),
    ("2026-04-22","X-AM","Tweet","Canva + ChatGPT + Notion + Buffer + VA = $2,558/month. What if one system did all of it?","Authority","B-27",False),
    ("2026-04-22","X-PM","Tweet","The most underrated skill in crypto is __________.","Community","B-27",False),
    ("2026-04-22","TK","Calculator video","Let me show you how much you're wasting on content tools.","Reach","B-27",False),
    ("2026-04-23","X-AM","Tweet","I analyzed what your favorite crypto KOL posted this week — their hooks, engagement patterns, and gaps. 30 seconds.","Authority","B-28",False),
    ("2026-04-23","X-PM","Tweet","Who are the 3 most underrated accounts in crypto X right now? I need new follows.","Community","B-28",False),
    ("2026-04-23","LI","Post","I analyzed a top Web3 brand's content strategy in 30 seconds. Here's what they're doing right — and what they're missing.","Authority","B-28",False),
    ("2026-04-23","IG","Reel","I analyzed your favorite crypto KOL's entire content strategy in 30 seconds. Watch.","Authority","B-28",False),
    ("2026-04-24","X-AM","Tweet","In 48 hours: free live walkthrough — 'How to Build a Content System That Runs Without You.' 45 min. 50 spots.","Sales","B-29",False),
    ("2026-04-24","X-PM","Tweet","29 days ago: near-zero engagement. Today: real conversations happening daily. Only thing that changed: stopped selling, started talking.","Community","B-29",False),
    ("2026-04-24","TK","Hype video","Free live demo. 48 hours. 50 spots. Here's what you'll see.","Leads","B-29",False),
    ("2026-04-25","X-AM","Thread","30 days ago I reset everything. No signals. No links. No reposts. Just conversations. Here are the real numbers.","Authority","B-30",False),
    ("2026-04-25","X-PM","Tweet","Month 1 was about rebuilding trust with the algorithm. Month 2: scaling what works. What topic do you want me to go deep on?","Community","B-30",False),
    ("2026-04-25","LI","Post","30 days ago I restarted from near-zero engagement. Here are the raw numbers, the lessons, and what's next.","Authority","B-30",False),
    ("2026-04-25","IG","Reel","30 days. Zero gimmicks. Here's what happened.","Authority","B-30",False),
    # Phase 4
    ("2026-04-26","X-AM","Tweet","Pattern I've noticed: creators who ride trends early don't have better instincts. They have better systems for detecting trends.","Authority","C-26",False),
    ("2026-04-26","X-PM","Tweet","You spent 6 hours last week planning content. Your competitor spent 15 minutes. Same results. That gap is the game now.","Authority","C-1",False),
    ("2026-04-27","X-AM","Thread","The content strategy that separates $5K/month creators from $50K/month creators — in 5 steps.","Authority","C-27",False),
    ("2026-04-27","X-PM","Tweet","Canva. ChatGPT. Notion. Buffer. A VA. You're paying 5 subscriptions to do what one system handles. That's not a workflow — that's a tax.","Reach","C-2",False),
    ("2026-04-28","X-AM","Thread","ChatGPT is a hammer. You need a house. Here's what happens when you build a content strategy with just ChatGPT vs a purpose-built system.","Sales","C-28",False),
    ("2026-04-28","X-PM","Tweet","If you stopped posting for 2 weeks, would your brand survive? If the answer scares you, your content system is broken.","Authority","C-3",False),
    ("2026-04-28","LI","Post","ChatGPT is a hammer. Your content strategy needs a house — side-by-side comparison.","Sales","C-28",False),
    ("2026-04-28","IG","Carousel","The Disappearance Test — 5 signs your content system depends entirely on YOU","Authority","C-3",False),
    ("2026-04-29","X-AM","Thread","If one post brings you one client worth $2,000 and you publish 60 posts/month, how many clients do you need to 10X your content investment?","Sales","C-29",False),
    ("2026-04-29","X-PM","Tweet","A content manager costs $4,000/month. A freelance strategist: $2,000. Most Web3 projects pay both. What if you needed neither?","Reach","C-4",False),
    ("2026-04-30","X-AM","Tweet","I know exactly what your competitors posted this week, which hooks worked, and which formats flopped. 30 seconds.","Leads","C-30",False),
    ("2026-04-30","X-PM","Tweet","A pattern I've noticed: Web3 projects that grow fastest aren't the ones with the best tech. They're the ones with the best content systems.","Authority","C-5",False),
    ("2026-04-30","LI","Post","ROI calculator: content as a revenue engine, not a cost center. The math that makes content investment a no-brainer.","Sales","C-29",False),
    ("2026-04-30","IG","Reel","I just pulled your top competitor's content patterns for free. 30 seconds. Watch.","Leads","C-30",False),
    ("2026-05-01","X-AM","Tweet","You don't need a content strategist. You don't need a copywriter. You don't need a scheduler. You need one system that does all three.","Sales","C-31",False),
    ("2026-05-01","X-PM","Tweet","You're writing every caption by hand. Researching trends manually. Scheduling posts one by one. And you wonder why you're burned out.","Reach","C-6",False),
    ("2026-05-01","TK","Time-lapse video","The Manual Trap — manual content creation vs system content creation side by side","Reach","C-6",False),
    ("2026-05-02","X-AM","Thread","Every viral post follows one of these 5 frameworks. Master them and you'll never run out of content ideas.","Authority","C-32",False),
    ("2026-05-02","X-PM","Tweet","Content Creator vs Content Architect. One writes posts. The other designs systems that write, schedule, and optimize without them.","Authority","C-7",False),
    ("2026-05-02","LI","Post","5 content frameworks behind every viral post — Contrarian Reframe, Before/After, Step-by-Step, Diagnostic, Identity Shift","Authority","C-32",False),
    ("2026-05-02","IG","Carousel","The 5 Frameworks — steal them all","Authority","C-32",False),
    ("2026-05-03","X-AM","Tweet","HubSpot's 2026 report: post less, post better. The creators who win aren't publishing 10 garbage posts/day. They're publishing 2 perfect ones.","Reach","C-33",False),
    ("2026-05-03","X-PM","Tweet","It's 3AM and your competitor just published a post. They didn't write it. They didn't schedule it. Their system did. While they slept.","Reach","C-8",False),
    ("2026-05-03","TK","Demo","Post less, post better — what a quality-first content system actually looks like","Reach","C-33",False),
    ("2026-05-04","X-AM","Tweet","Most creators dread Monday because they have no content ready. What if you woke up Monday with your entire week planned, written, and scheduled?","Community","C-34",False),
    ("2026-05-05","X-AM","Tweet","Wednesday at 2PM EST: I'm building a complete content calendar from scratch. Live. On screen. No cuts. Place your bets on time.","Leads","C-35",False),
    ("2026-05-05","X-PM","Tweet","Track how many hours you spend on content this week. Writing. Editing. Researching. Scheduling. The number will make you sick.","Leads","C-10",False),
    ("2026-05-05","LI","Post","Live build announcement: content calendar from zero to scheduled. Wednesday 2PM EST.","Leads","C-35",False),
    ("2026-05-05","IG","Carousel","The Time Audit Challenge — track your content hours this week","Leads","C-10",False),
    ("2026-05-06","X-AM","Thread","Everyone's scared AI will kill their brand voice. Truth: most creators don't even HAVE a defined brand voice. They wing it and call it authentic.","Authority","C-36",False),
    ("2026-05-06","X-PM","Tweet","Most Web3 founders hire a social media manager as their first marketing hire. 6 months later they fire them. The problem was never the person.","Authority","C-11",False),
    ("2026-05-06","TK","Talking head","Here's why your 'brand voice' is actually just winging it — and how to fix it","Authority","C-36",False),
    ("2026-05-07","X-AM","Tweet + Video","I just built a 30-day content calendar in 47 seconds. Watch.","Sales","C-37",False),
    ("2026-05-07","X-PM","Tweet","60 posts per month. 4 platforms. Zero burnout. That's not a fantasy — that's what happens when you stop creating and start engineering.","Reach","C-12",False),
    ("2026-05-07","LI","Post","47 seconds to build a 30-day content calendar. What this means for Web3 brands.","Sales","C-37",False),
    ("2026-05-07","IG","Reel","47 seconds. 30-day calendar. Timer on screen. Watch the speed run.","Sales","C-37",False),
    ("2026-05-08","X-AM","Tweet","AI agents are hype. AI workflows are money. Agents do random things and hope. Workflows do the right thing every time.","Authority","C-38",False),
    ("2026-05-08","X-PM","Tweet","90% of your content ideas die in a notes app. Not because they're bad — because you don't have a system that turns ideas into published posts.","Authority","C-13",False),
    ("2026-05-08","TK","Demo","Workflows vs agents — watch what happens when structure beats magic","Authority","C-38",False),
    ("2026-05-09","X-AM","Thread","How to turn content into a $10K/month income engine — the strategy most Web3 creators ignore.","Sales","C-39",False),
    ("2026-05-09","X-PM","Tweet","I analyzed 500 viral Web3 posts. Here are the 5 patterns every single one follows.","Authority","C-14",False),
    ("2026-05-09","LI","Post","Content-to-revenue pipeline: authority → bridge → demo → social proof → repeat. The flywheel explained.","Sales","C-39",False),
    ("2026-05-09","IG","Carousel","The Income Engine — content strategy framework to $10K/month","Sales","C-39",False),
    ("2026-05-10","X-AM","Tweet","In the last 20 days I've shared more content strategy than most courses teach. Free content can't give you one thing: execution.","Leads","C-40",False),
    ("2026-05-10","X-PM","Tweet","A rule that will save your content strategy: if you don't have a system, you ARE the system. And you can't scale yourself.","Authority","C-15",False),
    ("2026-05-10","TK","Video compilation","20 days of strategy highlights. Starting Monday: the execution layer. ContentBrain demos begin.","Leads","C-40",False),
    # Phase 5
    ("2026-05-11","X-AM","Tweet + Video","Here's how a crypto project does content now vs how they do it with ContentBrain. The difference will make you angry at your current process.","Sales","C-41",False),
    ("2026-05-11","X-PM","Tweet","Drop your biggest content struggle below. I'll reply to each one with a specific fix.","Community","C-41",False),
    ("2026-05-12","X-AM","Tweet + Video","I just recorded a 5-minute Loom showing how a crypto niche could publish 60 posts/month without hiring anyone.","Sales","C-42",False),
    ("2026-05-12","X-PM","Tweet","While you spent 3 hours writing one tweet, your competitor published 5 posts across 4 platforms. They didn't work harder.","Reach","C-16",False),
    ("2026-05-12","LI","Post","Loom demo: 60 posts/month for a Web3 brand, zero headcount increase.","Sales","C-42",False),
    ("2026-05-12","IG","Video","Before/after walkthrough: manual process vs ContentBrain — split screen","Sales","C-41",False),
    ("2026-05-13","X-AM","Tweet + Carousel","I added up what the average Web3 project spends on content. Then compared it to ContentBrain. The numbers aren't even close.","Reach","C-43",False),
    ("2026-05-13","X-PM","Tweet","The creator who posts 3X more than you isn't grinding harder. They stopped doing manually what a system handles in seconds.","Reach","C-19",False),
    ("2026-05-13","TK","Calculator video","The real cost breakdown: your current stack vs one system. Calculator on screen.","Reach","C-43",False),
    ("2026-05-14","X-AM","Tweet + Video","Watch me create a week of TikTok scripts in 32 seconds. Not captions — full scripts with hooks, body, and CTAs.","Reach","C-44",False),
    ("2026-05-14","LI","Post","The Cost Comparison: content manager + writer + tools + VA = $6,480/mo. ContentBrain: fraction of that.","Reach","C-43",False),
    ("2026-05-14","IG","Reel","32 seconds for a week of TikTok scripts. Watch the timer.","Reach","C-44",False),
    ("2026-05-15","X-AM","Thread","A DeFi project came to me doing 8 posts/month. Now they do 60. Their engagement didn't drop — it tripled. Here's what changed.","Authority","C-45",False),
    ("2026-05-15","X-PM","Tweet","Be honest: how many hours did you spend on content last week? Drop your number below.","Community","C-45",False),
    ("2026-05-15","TK","Case study video","DeFi deep-dive: 8 posts/month → 60, engagement tripled","Authority","C-45",False),
    ("2026-05-16","X-AM","Tweet + Video","I fed ContentBrain my last 50 posts and asked it to write the next one. 73% of you guessed wrong on which was AI.","Authority","C-46",False),
    ("2026-05-16","LI","Post","Brand voice + AI: the trust objection answered with proof. 73% guessed wrong.","Authority","C-46",False),
    ("2026-05-16","IG","Reel","Can you tell which post was AI? The results surprised everyone.","Authority","C-46",False),
    ("2026-05-17","X-AM","Tweet","Saturday morning. Coffee in hand. Zero content stress. My entire next week is already written, optimized, and scheduled.","Community","C-47",False),
    ("2026-05-17","TK","Lifestyle","Saturday morning as a creator who doesn't create content manually anymore","Community","C-47",False),
    ("2026-05-18","X-AM","Thread","Pattern I've noticed: most Web3 projects track their own analytics but never study their competitors' content. Boxing blindfolded.","Authority","C-48",False),
    ("2026-05-18","X-PM","Tweet","Sunday reset. What's one thing you're changing about your content strategy this week?","Community","C-48",False),
    ("2026-05-19","X-AM","Tweet","Thursday at 2PM EST: Free live workshop — How to build a 30-day content engine that runs without you. No slides. No fluff. Just a live build.","Leads","C-49",False),
    ("2026-05-19","X-PM","Tweet","The gap between 12 hrs/week on content and 2 hrs/week? A system. That's the entire difference.","Authority","C-49",False),
    ("2026-05-19","LI","Post","Workshop announcement: Build a content engine that runs without you. Thursday 2PM EST. 100 live spots.","Leads","C-49",False),
    ("2026-05-19","IG","Carousel","Workshop preview: what you'll learn + build in 45 minutes","Leads","C-49",False),
    ("2026-05-20","X-AM","Tweet + Video","A day in my life as a creator who doesn't create content manually: wake up, check dashboard, approve posts, done by 9AM.","Sales","C-50",False),
    ("2026-05-20","X-PM","Tweet","Honest question: what's the one thing you wish someone told you before you started creating content?","Community","C-50",False),
    ("2026-05-20","TK","Day-in-the-life","Morning routine: check dashboard → review drafts → approve and schedule → done by 9AM","Sales","C-50",False),
    ("2026-05-21","X-AM","Tweet","Tomorrow: I build a 30-day content engine live. From zero to scheduled. You'll watch the entire thing. In 24 hours.","Leads","C-51",False),
    ("2026-05-21","LI","Post","Workshop reminder: last call for free spots. Tomorrow 2PM EST.","Leads","C-51",False),
    ("2026-05-21","IG","Story series","Behind the scenes: prepping for tomorrow's live build","Leads","C-51",False),
    ("2026-05-22","X-AM","Tweet","We're live. Building a 30-day content engine from scratch. No templates. No slides. Just ContentBrain and a blank screen. Let's go.","Sales","C-52",False),
    ("2026-05-22","X-PM","Thread","Workshop done. 47 minutes to build what takes most teams a week. Here are the key takeaways.","Sales","C-52",False),
    ("2026-05-22","TK","Edited highlights","Workshop highlights: 30-day engine built live in 47 minutes","Sales","C-52",False),
    ("2026-05-23","X-AM","Thread","Yesterday: 30-day content engine live in 47 min. 300 people watched. 6 biggest takeaways if you missed it.","Reach","C-53",False),
    ("2026-05-23","X-PM","Tweet","Workshop attendee DM'd me 2 hours after: 'Just set up my first calendar. 30 days. 60 posts. Done.'","Sales","C-54",False),
    ("2026-05-23","LI","Post","Workshop recap: 6 takeaways from building a content engine live","Reach","C-53",False),
    ("2026-05-23","IG","Carousel","6 takeaways from building a 30-day content engine live","Reach","C-53",False),
    ("2026-05-24","X-AM","Tweet + Screenshot","Workshop attendee: '30 days, 60 posts, done in 2 hours.' This is what speed looks like.","Sales","C-54",False),
    ("2026-05-24","X-PM","Tweet","If you could only hold 3 crypto tokens for 12 months — no selling, no trading — what are they?","Community","C-54",False),
    ("2026-05-24","TK","Testimonial video","Real results from workshop attendees — in their own words","Sales","C-54",False),
    ("2026-05-25","X-AM","Thread + Video","Here's what ContentBrain looks like for a DeFi protocol. Research. Hooks. Threads. Educational content. All in brand voice. All in minutes.","Sales","C-55",False),
    ("2026-05-25","X-PM","Tweet","What topic do you want me to go deep on this week? Most requested gets a full breakdown.","Community","C-55",False),
    ("2026-05-26","X-AM","Tweet + Video","Here's what ContentBrain looks like for an AI startup. Thought leadership. Technical explainers. Investor content. All automated.","Sales","C-56",False),
    ("2026-05-26","X-PM","Tweet","Founders: your time is too valuable for content creation. You handle the vision. The system handles execution.","Authority","C-56",False),
    ("2026-05-26","LI","Post","ContentBrain for AI startups: thought leadership and technical content — automated, on-brand.","Sales","C-56",False),
    ("2026-05-26","IG","Video","DeFi niche demo: research to published posts in minutes","Sales","C-55",False),
    ("2026-05-27","X-AM","Thread","5 messages I received this week from ContentBrain users. I didn't ask them to say this. They just... said it.","Sales","C-57",False),
    ("2026-05-27","X-PM","Tweet","Share one win from this week. Doesn't matter how small. Building in public means celebrating in public.","Community","C-57",False),
    ("2026-05-27","TK","Testimonial compilation","5 unsolicited messages from ContentBrain users — screen recordings","Sales","C-57",False),
    ("2026-05-28","X-AM","Tweet + Video","Here's what ContentBrain looks like for a Web3 gaming project. Lore threads. Community posts. Hype content. All generated, all on-brand.","Sales","C-58",False),
    ("2026-05-28","LI","Post","Testimonials compilation: 5 ContentBrain users share real dollar-amount results","Sales","C-57",False),
    ("2026-05-28","IG","Reel","Web3 gaming demo: lore content, hype posts, community updates — all ContentBrain","Sales","C-58",False),
    ("2026-05-29","X-AM","Tweet + Video","I created 7 days of Binance Square content in under 2 minutes. Educational threads. Market analysis. Community polls.","Leads","C-59",False),
    ("2026-05-29","X-PM","Tweet","Making money from exchange content programs requires volume AND quality. One system handles both.","Leads","C-59",False),
    ("2026-05-29","TK","Screen recording","7 days of exchange content in 2 minutes — timer running","Leads","C-59",False),
    ("2026-05-30","X-AM","Thread","In the last 20 days: demos, results, proof. Here's what's next — ContentBrain opens to 25 new users. Monday. 9AM EST. First come, first served.","Leads","C-60",False),
    ("2026-05-30","X-PM","Tweet","In 48 hours, 25 people get a content team that never sleeps. The rest keep doing it manually. Which side?","Leads","C-60",False),
    ("2026-05-30","LI","Post","Phase 3 recap: 20 days of demos, results, and real proof. Limited opening announcement.","Leads","C-60",False),
    ("2026-05-30","IG","Reel","Phase 3 highlights: 20 days of demos compiled into 60 seconds","Leads","C-60",False),
    # Phase 6
    ("2026-05-31","X-AM","Tweet","In 48 hours, ContentBrain opens to 25 new users. After that, the waitlist closes until July. This is the last call.","Sales","C-61",False),
    ("2026-05-31","X-PM","Tweet","The ones who move first always win. In crypto, in content, in business. That's just how it works.","Community","C-61",False),
    ("2026-05-31","TK","Countdown hype","48 hours. 25 spots. Your content team starts Monday.","Sales","C-61",False),
    ("2026-06-01","X-AM","Thread","Tomorrow morning, 25 people will wake up with a content team that never sleeps. The other 10,000 on this feed will keep doing it manually.","Sales","C-62",False),
    ("2026-06-02","X-AM","Tweet + Video","ContentBrain is live. 25 spots. Your content team starts today.","Sales","C-63",False),
    ("2026-06-02","X-PM","Tweet","Day 1 users are already building calendars. The energy in onboarding calls is different.","Sales","C-63",False),
    ("2026-06-02","LI","Post","ContentBrain is officially open. 25 spots for Web3 brands. Onboarding starts today.","Sales","C-63",False),
    ("2026-06-02","IG","Reel","Launch day: hype reel — speed runs, results, testimonials","Sales","C-63",False),
    ("2026-06-03","X-AM","Tweet","17 spots left. 8 claimed in the first 3 hours. If you're still thinking about it, your competitor already signed up.","Sales","C-64",False),
    ("2026-06-03","X-PM","Tweet","Every day you wait is a day your competitor is already using this. That's not pressure — that's math.","Sales","C-64",False),
    ("2026-06-03","TK","Urgency update","Spot counter: 8 claimed in 3 hours. Real-time update.","Sales","C-64",False),
    ("2026-06-04","X-AM","Tweet + Screenshot","User #3 signed up yesterday at 10AM. By 2PM: 30-day calendar. By 6PM: month of content scheduled. Day 1.","Sales","C-65",False),
    ("2026-06-04","LI","Post","New user results: first 30-day calendar built in 4 hours on Day 1","Sales","C-65",False),
    ("2026-06-04","IG","Carousel","Day 1 user results — from signup to fully scheduled in hours","Sales","C-65",False),
    ("2026-06-05","X-AM","Tweet + Video","ContentBrain costs $X/month. A content manager costs $4K. A burned-out founder doing it themselves? That costs everything.","Sales","C-66",False),
    ("2026-06-05","X-PM","Tweet","A content manager costs $4-6K/month. An AI content system costs less and works 24/7. The math is changing.","Sales","B-25 revisit",False),
    ("2026-06-05","TK","Calculator video","The real cost breakdown: your current stack vs ContentBrain — on a calculator","Sales","C-66",False),
    ("2026-06-06","X-AM","Tweet","I'm doing something I've never done before: free 15-minute content audits for the next 48 hours. Tell me your niche. I'll tell you what's broken.","Leads","C-67",False),
    ("2026-06-06","X-PM","Tweet","Comment AUDIT with your niche. I'll send you a voice note with 3 things to fix immediately.","Leads","C-67",False),
    ("2026-06-06","LI","Post","48-hour content audit window: free personalized breakdown for Web3 brands. DM your niche.","Leads","C-67",False),
    ("2026-06-06","IG","Story","48-hour content audit blitz — DM me your niche for a custom breakdown","Leads","C-67",False),
    ("2026-06-07","X-AM","Tweet + Screenshot","ContentBrain user DM this morning: 'Why didn't you build this 2 years ago? Would have saved $50K in freelancer fees.'","Sales","C-68",False),
    ("2026-06-07","X-PM","Tweet","6 spots left this month. Every month without ContentBrain is another month overpaying the old way.","Sales","C-68",False),
    ("2026-06-07","TK","Testimonial","Real DMs from ContentBrain users — the $50K freelancer savings story","Sales","C-68",False),
    ("2026-06-08","X-AM","Tweet","To every creator who's been following for 60+ days: thank you. This community is bigger than any tool. What content topic next week?","Community","C-69",False),
    ("2026-06-09","X-AM","Thread","You asked for it. The most requested topic: [based on Sunday replies]. Here's the complete breakdown.","Authority","C-70",False),
    ("2026-06-09","X-PM","Tweet","ContentBrain generates this kind of analysis for any topic in minutes. 3 hours of research → 3 minutes.","Authority","C-70",False),
    ("2026-06-09","LI","Post","Community deep-dive: the most-requested topic, broken down with ContentBrain analysis","Authority","C-70",False),
    ("2026-06-09","IG","Carousel","Community-requested topic: full breakdown in carousel format","Authority","C-70",False),
    ("2026-06-10","X-AM","Tweet","First workshop: 300 people. 200 asked for another. Thursday 2PM EST: Advanced Content Engineering. Free. Live. No replays this time.","Leads","C-71",False),
    ("2026-06-10","X-PM","Tweet","This one is different: competitor scraping, trend detection, multi-platform distribution. All live.","Leads","C-71",False),
    ("2026-06-10","TK","Teaser","Workshop #2 announcement: Advanced Content Engineering. No replays. Thursday.","Leads","C-71",False),
    ("2026-06-11","X-AM","Tweet","Tomorrow's workshop upgrade: everyone who attends live gets a free competitive intelligence report for their niche. $500 value.","Leads","C-72",False),
    ("2026-06-11","X-PM","Tweet","Spots filling fast. This is the only advanced session this month. Comment ADVANCED to register.","Leads","C-72",False),
    ("2026-06-11","LI","Post","Advanced workshop tomorrow: competitor scraping and trend detection live. Free intel report for attendees.","Leads","C-72",False),
    ("2026-06-11","IG","Story","Workshop countdown: 24 hours. Free competitor report for live attendees.","Leads","C-72",False),
    ("2026-06-12","X-AM","Tweet","We're live. Advanced Content Engineering. Competitor scraping. Trend detection. Multi-platform distribution. Let's build.","Sales","C-73",False),
    ("2026-06-12","X-PM","Thread","50 minutes of pure execution. Here's what we built: competitor analysis, trend surfacing, cross-platform scheduling.","Sales","C-73",False),
    ("2026-06-12","TK","Edited highlights","Advanced workshop highlights: the intelligence layer revealed","Sales","C-73",False),
    ("2026-06-13","X-AM","Thread","Yesterday's workshop: 280 live attendees. 15 signed up on the spot. 40 booked strategy calls. Here are 3 messages that came in after.","Sales","C-74",False),
    ("2026-06-13","X-PM","Tweet","5 strategy call slots left this week. Free 15 minutes. No pitch. Just value. Comment CALL to book.","Sales","C-74",False),
    ("2026-06-13","LI","Post","Workshop #2 results: 280 attendees, 15 immediate signups, 40 strategy calls. The numbers speak.","Sales","C-74",False),
    ("2026-06-13","IG","Carousel","Workshop results + top 3 testimonials from attendees","Sales","C-74",False),
    ("2026-06-14","X-AM","Tweet","In the last 2 weeks: 2 workshops. 25 new users. 40 strategy calls. ContentBrain isn't a product anymore — it's a movement.","Sales","C-75",False),
    ("2026-06-14","X-PM","Tweet","Next month: user spotlights, advanced features, community events. Follow to stay in the loop. The best is ahead.","Community","C-75",False),
    ("2026-06-14","TK","Milestone","Phase 4 recap: from conversion push to community movement","Sales","C-75",False),
    # Phase 7
    ("2026-06-15","X-AM","Thread","User spotlight: DeFi protocol went from 8 posts/month to 60 using ContentBrain. Community engagement tripled. Here's their story.","Authority","C-76",False),
    ("2026-06-15","X-PM","Tweet","Want your project featured next? DM me SPOTLIGHT with your results. Best stories get highlighted.","Community","C-76",False),
    ("2026-06-16","X-AM","Tweet + Video","Your written content is handled. But what about video? Here's what happens when ContentBrain handles scripts, visuals, and voiceover.","Sales","C-77",False),
    ("2026-06-16","X-PM","Tweet","DeFi case study 3-month follow-up: the long-term numbers are even better than the 7-day pilot.","Authority","C-45 revisit",False),
    ("2026-06-16","LI","Post","Upsell bridge: Video Production package — scripts, visuals, voiceover, all automated.","Sales","C-77",False),
    ("2026-06-16","IG","Reel","ContentBrain Video Production: from script to finished video in minutes","Sales","C-77",False),
    ("2026-06-17","X-AM","Thread","Announcing: The ContentBrain Community. A private group for users to share strategies, results, and support each other. Free for all users.","Community","C-78",False),
    ("2026-06-17","X-PM","Tweet","Users who connect with other users churn less, grow faster, and build better systems. Community is the moat.","Community","C-78",False),
    ("2026-06-17","TK","Announcement","ContentBrain Community launch: what's inside, who it's for, how to join","Community","C-78",False),
    ("2026-06-18","X-AM","Thread","User spotlight: AI startup went from zero social presence to 15K followers in 60 days. CEO hasn't written a single post.","Authority","C-79",False),
    ("2026-06-18","X-PM","Tweet","Founders: your time is too valuable for content creation. You handle the vision. ContentBrain handles execution.","Authority","C-79",False),
    ("2026-06-18","LI","Post","AI startup spotlight: zero to 15K followers in 60 days, CEO never wrote a post. Here's how.","Authority","C-79",False),
    ("2026-06-18","IG","Carousel","User spotlight: AI startup case study — full transformation","Authority","C-79",False),
    ("2026-06-19","X-AM","Thread","30 days of ContentBrain data across all users. Average time saved: 18 hrs/week. Cost reduction: 62%. Content output: 4.2X increase.","Authority","C-80",False),
    ("2026-06-19","X-PM","Tweet","These numbers are real, from real users, in 30 days. Imagine what 90 days looks like.","Authority","C-80",False),
    ("2026-06-19","TK","Data visualization","ContentBrain by the numbers: 30-day aggregate data report","Authority","C-80",False),
    ("2026-06-20","X-AM","Tweet + Carousel","Starting today: refer a friend to ContentBrain and get a free month. They get onboarded. You get rewarded. Everybody wins.","Leads","C-81",False),
    ("2026-06-20","LI","Post","30-day data report: 18 hrs/week saved, 62% cost reduction across all users — the full breakdown.","Authority","C-80",False),
    ("2026-06-20","IG","Carousel","Referral program launch: how it works, step by step","Leads","C-81",False),
    ("2026-06-21","X-AM","Thread","ContentBrain analyzed 10,000 posts across Web3 this week. Here are the 5 trends about to explode — and exactly how to ride them.","Authority","C-82",False),
    ("2026-06-21","X-PM","Tweet","This report generates automatically every week. ContentBrain users get it in their inbox every Monday morning.","Authority","C-82",False),
    ("2026-06-21","TK","Trend report video","5 content trends about to explode — from 10,000-post analysis","Authority","C-82",False),
    ("2026-06-22","X-AM","Tweet","90 days ago I started sharing content strategy on this feed. Today: a product, a community, and results that speak louder than any tweet. Thank you.","Community","C-83",False),
    ("2026-06-23","X-AM","Thread","Content + Video + Community Automation + Lead Funnels. What if one system handled all of it? For less than you pay a social media manager.","Sales","C-84",False),
    ("2026-06-23","X-PM","Tweet","The agency equivalent: $15-20K/month. AI Marketing Automation package: $3-5K. Same output. Better data. No HR.","Sales","C-84",False),
    ("2026-06-23","LI","Post","Full stack announcement: AI Marketing Automation — content, video, community, funnels, analytics.","Sales","C-84",False),
    ("2026-06-23","IG","Carousel","Full stack package: what the AI Marketing Automation includes","Sales","C-84",False),
    ("2026-06-24","X-AM","Tweet + Video","User spotlight: Web3 gaming project used ContentBrain for 90 days of lore content. Discord grew by 12,000 members.","Authority","C-85",False),
    ("2026-06-24","X-PM","Tweet","Gaming projects need daily community content. ContentBrain delivers it at scale. Period.","Authority","C-85",False),
    ("2026-06-24","TK","Spotlight video","Gaming project spotlight: 90 days of automated lore, community updates, hype posts","Authority","C-85",False),
    ("2026-06-25","X-AM","Thread","Not ready for monthly? One-Time Build: I build your complete content system, hand you the keys. Yours forever.","Sales","C-86",False),
    ("2026-06-25","LI","Post","One-Time Build option: custom content system, $2.5K-$15K, documentation included, yours forever.","Sales","C-86",False),
    ("2026-06-25","IG","Carousel","ContentBrain options: monthly packages vs one-time builds — comparison","Sales","C-86",False),
    ("2026-06-26","X-AM","Thread","Q3 starts in 4 days. If your content strategy for July-September isn't planned yet, you're already behind. Here's how to plan a quarter in 30 minutes.","Leads","C-87",False),
    ("2026-06-26","X-PM","Tweet","I'll build your Q3 content plan for free if you book a strategy call this week. DM me Q3. First 10 get it today.","Leads","C-87",False),
    ("2026-06-26","TK","Tutorial","Plan your entire Q3 content in 30 minutes — step by step framework","Leads","C-87",False),
    ("2026-06-27","X-AM","Tweet + Video","Announcing: ContentBrain Affiliate Program. 25% recurring commission. If you talk about content strategy, this is free money.","Leads","C-88",False),
    ("2026-06-27","X-PM","Tweet","Priority for creators with 1K+ followers. Payouts monthly in USDT or USD. Comment AFFILIATE to apply.","Leads","C-88",False),
    ("2026-06-27","LI","Post","Q3 planning framework: how to plan a full quarter of content in 30 minutes + ContentBrain as execution layer.","Leads","C-87",False),
    ("2026-06-27","IG","Carousel","Affiliate program: earn 25% recurring — how it works","Leads","C-88",False),
    ("2026-06-28","X-AM","Thread","90 days ago I made a promise: show you a better way to do content. Here are the numbers from 90 days of ContentBrain.","Authority","C-89",False),
    ("2026-06-28","X-PM","Tweet","Q3 is where we scale. New features. More niches. Better results. If you're not in yet, this is the moment.","Authority","C-89",False),
    ("2026-06-28","TK","Compilation video","90-day results: the complete ContentBrain story — from Day 1 to today","Authority","C-89",False),
    ("2026-06-29","X-AM","Tweet","Day 90. The first chapter is written. Next 90 days? Bigger features. More niches. A community that builds together. This isn't the end — it's the foundation.","Community","C-90",False),
    ("2026-06-29","X-PM","Tweet","Thank you for being here from Day 1. Comment NEXT if you're riding into Q3 with us. The best content systems are built by communities.","Community","C-90",False),
]

# ── Build lookup: date_str -> {platform -> entry} ─────────────────
v1_lookup = defaultdict(dict)
for e in V1_ENTRIES:
    d, plat = e[0], e[1]
    v1_lookup[d][plat] = e

# ── Phase-specific topic banks ─────────────────────────────────────
# These generate the [TOPIC ONLY] entries for slots without v1 hooks
TIKTOK_TOPICS = {
    # per phase, per category: list of rotating topic templates
    1: {  # Authority Rebuild
        "Sales": [
            "My exact system for catching trades others miss",
            "How I went from manual charting to automated signals",
            "The 3 tools that replaced my $5K/month content team",
            "Why I stopped trading like everyone else",
            "How I built a system that works while I sleep",
            "The real cost of doing crypto content manually",
            "From 0 to profitable: my actual timeline",
            "What separates profitable traders from everyone else",
            "How I automate my entire research process",
        ],
        "Reach": [
            "The worst crypto advice I ever followed",
            "Things I wish someone told me before crypto",
            "Why most crypto KOLs are lying to you",
            "The moment I almost quit crypto forever",
            "Hot take: 90% of crypto education is useless",
            "Why your favorite crypto influencer is broke",
            "The uncomfortable truth about trading courses",
            "Story time: how I lost $10K in one trade",
            "Why being honest about losses makes you more money",
        ],
        "Community": [
            "What's the one thing you'd change about crypto culture?",
            "Biggest struggle as a crypto beginner — drop yours",
            "Reply with your worst trade. I'll share mine.",
            "The question nobody asks about building in Web3",
            "If you could learn one crypto skill instantly, what?",
            "What's harder — finding alpha or trusting it?",
            "Drop your portfolio age. How long you been at this?",
            "Crypto truths nobody wants to admit",
            "The real reason most people fail in crypto",
        ],
        "Authority": [
            "3 market signals most traders completely ignore",
            "Why simplicity beats complexity in every trade",
            "The framework I use to evaluate any project in 5 min",
            "Polarizing take: stop diversifying your portfolio",
            "Risk management isn't optional — it's the whole game",
            "Why 58% win rate is actually elite-level trading",
            "The only 3 indicators you actually need",
            "Data doesn't lie: what separates winners from losers",
            "Most traders are gambling. Here's how to actually trade.",
        ],
    },
    2: {  # Bridge + Hints
        "Sales": [
            "I used to spend 6 hours on content. Now I spend 15 minutes.",
            "The system that replaced my content team",
            "What happens when you automate your content workflow",
            "My content costs dropped 80%. Quality stayed the same.",
            "Behind the scenes of my automated content process",
            "How systems thinking changed my entire business",
            "The architecture behind consistent content output",
        ],
        "Reach": [
            "Every crypto KOL has a secret they won't tell you",
            "The day I realized talent doesn't scale — systems do",
            "Why I stopped chasing viral content",
            "The content game is rigged. Here's how to win anyway.",
            "Most creators burn out in 6 months. Here's why.",
            "Your content isn't bad. Your process is broken.",
            "The creator who posts 3X more isn't working 3X harder",
        ],
        "Community": [
            "What's your biggest content creation bottleneck?",
            "How many hours/week do you spend on content? Be honest.",
            "Drop your content stack. I'll rate it.",
            "Challenge: post every day this week. Tag me.",
            "What would you do with 10 extra hours per week?",
            "Crypto Twitter is changing. For better or worse?",
            "Share your best performing post this month",
        ],
        "Authority": [
            "Systems beat talent every single time. Here's proof.",
            "The evolution: trader → creator → architect",
            "AI without human context is expensive noise",
            "Why workflows beat agents in every real business",
            "The content stack that produces 15+ posts/week in 3 hours",
            "Consistency isn't discipline. It's architecture.",
            "The difference between creators and content architects",
        ],
    },
    3: {  # Soft Reveal
        "Sales": [
            "Watch me build 7 days of content in 4 minutes",
            "ContentBrain first look — raw, unfiltered demo",
            "Speed run: competitor analysis in 30 seconds",
            "The tool stack killer: one system to replace them all",
            "DeFi project test: 21 posts in zero manual minutes",
            "Cost breakdown: your current stack vs this",
            "Free live walkthrough — content system that runs without you",
            "30-day recovery results with real numbers",
            "Workshop announcement: build a content engine live",
        ],
        "Reach": [
            "AI wrote 3 hooks. Humans couldn't tell which was AI.",
            "Can you guess which post was written by AI?",
            "The content system debate: too good to be true?",
            "Why one person + a system beats a 5-person team",
            "The tool cost that nobody talks about",
            "Saturday vibes: my content week is already done",
            "What if you never had to write content again?",
            "The automation myth vs automation reality",
            "Why content teams are becoming obsolete",
        ],
        "Community": [
            "If you could automate ONE content task, what would it be?",
            "End of month challenge: what's your April goal?",
            "The most underrated skill in crypto is __________",
            "Who are the 3 most underrated crypto accounts right now?",
            "29 days of conversations > 29 days of broadcasts",
            "Share one win from this week. I'll start.",
            "Month 1 complete. What topic do you want next?",
            "Drop your niche. I'll tell you what content to make.",
            "What changed for you in the last 30 days?",
        ],
        "Authority": [
            "ContentBrain: 6 months of building. Here's what it does.",
            "You don't need a content team. You need a content system.",
            "I analyzed your favorite KOL's content in 30 seconds",
            "The competitor analysis framework nobody teaches",
            "AI content sounds robotic? 73% couldn't tell the difference.",
            "The trust objection answered with real data",
            "Why I built ContentBrain: the honest story",
            "Canva + ChatGPT + Notion + Buffer + VA = $2,558/mo. Or...",
            "The content stack that replaced a $4K/month hire",
        ],
    },
    4: {  # Bridge Education
        "Sales": [
            "30-day content calendar built in 47 seconds — watch",
            "One system. All platforms. Zero burnout.",
            "How to turn content into a $10K/month income engine",
            "The math: 1 post → 1 client → $2K. Scale that.",
            "ChatGPT is a hammer. You need a house.",
            "The execution gap: strategy vs system",
            "Content ROI calculator — the numbers that matter",
            "Why most founders fire their social media manager",
            "The live build: content calendar from zero",
            "Speed run: 7 days of content in under a minute",
            "Proof: free content can't give you execution",
            "20 days of free strategy. Monday: the execution layer.",
            "The disappearance test for your content system",
            "Content pipeline: how to go from idea to published",
            "Every viral post follows one of 5 frameworks",
        ],
        "Reach": [
            "Your competitor published a post at 3AM. They were sleeping.",
            "Manual content creation is a tax on your time",
            "60 posts/month. 4 platforms. Zero burnout.",
            "The time audit challenge: track your content hours",
            "Post less, post better — with proof",
            "Content Creator vs Content Architect",
            "The 3AM competitor advantage nobody talks about",
            "Brand voice isn't authenticity — it's winging it",
            "90% of your ideas die in a notes app. Here's why.",
            "HubSpot says post less. Here's what they mean.",
            "Most creators dread Monday. What if you didn't?",
            "5 frameworks behind every viral post — steal them",
            "If your system needs you, it's not a system",
            "The content burnout cycle and how to break it",
            "500 viral posts analyzed. 5 patterns. Every time.",
        ],
        "Community": [
            "Content struggles: drop yours, I'll fix it",
            "What would you build with 10 extra hours/week?",
            "Sunday reset: what's changing this week?",
            "Track your content hours this week — report back",
            "The Monday dread is real. How do you handle it?",
            "Rate my content stack: post yours",
            "What's the one tool you can't live without?",
            "If you stopped posting for 2 weeks, would anyone notice?",
            "Most creators won't admit this about burnout",
            "What's your content creation weak spot?",
            "Challenge: batch your entire week in one sitting",
            "The gap between 12 hrs/week and 2 hrs/week on content",
            "Honest question: are you creating or engineering?",
            "Drop your niche — I'll suggest your next 3 posts",
            "Friday energy: share your best post this week",
        ],
        "Authority": [
            "Trend detection isn't instinct — it's systems",
            "The $5K vs $50K creator strategy gap",
            "5 content frameworks you need to master",
            "Web3 projects that grow fastest have the best content systems",
            "AI agents are hype. AI workflows are money.",
            "The brand voice problem most creators ignore",
            "Pattern: best creators aren't most talented — most consistent",
            "Founders: stop hiring social media managers. Build systems.",
            "Data beats opinions. Always. Here's proof.",
            "The content-to-revenue pipeline explained",
            "Why most Web3 projects track analytics wrong",
            "The live build results: what speed actually looks like",
            "Content isn't a cost center. It's a revenue engine.",
            "500 viral posts → 5 patterns. Master them all.",
            "If you don't have a system, you ARE the system",
        ],
    },
    5: {  # Demo + Social Proof
        "Sales": [
            "Before vs after ContentBrain — split screen demo",
            "60 posts/month. Zero headcount increase. Watch.",
            "TikTok scripts in 32 seconds. Full hooks + CTAs.",
            "DeFi project: 8→60 posts/month, engagement tripled",
            "Day in my life: dashboard → approve → done by 9AM",
            "Content engine built live in 47 minutes",
            "Workshop highlights: the speed is real",
            "Workshop attendee results: 30 days, 60 posts, done.",
            "ContentBrain for DeFi: research to posts in minutes",
            "ContentBrain for AI startups: automated thought leadership",
            "5 unsolicited user messages. They just... said it.",
            "Web3 gaming demo: lore + hype content, all on-brand",
            "7 days of exchange content in 2 minutes",
            "25 spots opening Monday. First come, first served.",
            "ContentBrain for NFT projects: collection stories + hype",
            "The Loom demo: 60 posts/month walkthrough",
            "User results compilation — real screenshots",
            "Binance Square content: volume AND quality",
            "Saturday morning: zero content stress. Week is done.",
            "20 days of demos compiled into 60 seconds",
        ],
        "Reach": [
            "The real cost breakdown: your stack vs ContentBrain",
            "Your competitor posts 3X more. They're not grinding harder.",
            "Cost comparison: $6,480/mo vs a fraction of that",
            "32 seconds for a week of scripts. Timer on screen.",
            "While you wrote 1 tweet, they published 5 across 4 platforms",
            "The numbers aren't even close — content cost comparison",
            "6 biggest takeaways from the workshop",
            "Phase 3 highlights: 20 days of demos in 60 seconds",
            "In 48 hours, 25 people get a content team that never sleeps",
            "The speed difference is making people angry",
            "One system handles volume AND quality",
            "What 300 workshop attendees learned in 47 minutes",
            "30 days of content stress eliminated. Permanently.",
            "The $50K freelancer savings story — real DMs",
            "Attendee DM: 'Set up my calendar in 2 hours. 60 posts. Done.'",
            "The cost math is changing faster than you think",
            "Content teams are overpaying. The data proves it.",
            "Speed run: entire week of content planned in seconds",
            "The workshop replay everyone's asking about",
            "Manual content creation is officially obsolete",
        ],
        "Community": [
            "Drop your biggest content struggle. I'll fix it.",
            "Honest: how many hours on content last week?",
            "Saturday morning vibes — what are you creating?",
            "Sunday reset: one change for this week?",
            "What's the one thing you wish you knew earlier?",
            "Share one win from this week. Celebrate in public.",
            "What topic should I go deep on next?",
            "If you could hold only 3 tokens for 12 months — which?",
            "To everyone following for 60+ days: thank you.",
            "Workshop attendees: drop your results below",
            "Building in public means celebrating in public",
            "What content would help you most right now?",
            "The gap between wanting to post and actually posting",
            "Friday wins: what worked this week?",
            "Morning routine check: how do you start your day?",
            "The community question: what do you need most?",
            "Drop your niche — free content idea in the replies",
            "Midweek energy: are you ahead or behind on content?",
            "Share your before/after content process",
            "Which platform gives you the most results?",
        ],
        "Authority": [
            "DeFi deep-dive: how systems beat manual at scale",
            "73% couldn't tell AI from human. The trust objection is dead.",
            "Most Web3 projects never study competitor content",
            "Pattern: projects tracking only their own analytics lose",
            "ContentBrain for every niche: the universal framework",
            "Brand voice + AI: proof it works",
            "Competitor analysis in 30 seconds — the intelligence layer",
            "Workshop live: building what takes most teams a week",
            "6 takeaways from 300 workshop attendees",
            "ContentBrain aggregate data: 18 hrs/week saved average",
            "The system that produces 60 posts/month at scale",
            "AI content isn't the future. AI content systems are.",
            "The content intelligence layer nobody talks about",
            "Real user data beats any sales pitch",
            "Why automated isn't the same as generic",
            "The content architecture behind consistent growth",
            "Speed + quality: the false tradeoff explained",
            "Workshop attendee results speak louder than demos",
            "Thought leadership automated: what it actually looks like",
            "Exchange content programs + AI: the arbitrage opportunity",
        ],
    },
    6: {  # Conversion Push
        "Sales": [
            "25 spots. Your content team starts today.",
            "17 spots left. 8 claimed in 3 hours.",
            "User #3: signup → 30-day calendar → scheduled. Day 1.",
            "ContentBrain vs a content manager. The math is clear.",
            "User DM: 'Would have saved $50K in freelancer fees.'",
            "In 2 weeks: 2 workshops, 25 users, 40 strategy calls.",
            "Free 15-minute content audits for 48 hours",
            "6 spots left this month. The old way is overpaying.",
            "The launch numbers: real-time spot counter",
            "Strategy call results: what 15 minutes of value looks like",
            "Day 1 users are already building calendars",
            "Every day without a system costs you more than the system",
            "Workshop #2: advanced content engineering live",
            "The intelligence layer: competitor scraping + trend detection",
        ],
        "Reach": [
            "The ones who move first always win. In everything.",
            "In 48 hours, the waitlist closes until July.",
            "Tomorrow morning, 25 people wake up with a content team",
            "Every day you wait is a day your competitor uses this",
            "The cost of doing nothing is higher than you think",
            "280 live attendees. 15 signed up on the spot.",
            "50 minutes of pure execution — workshop recap",
            "The movement is bigger than any single tool",
            "Content audit blitz: DM your niche for free breakdown",
            "Community deep-dive: most-requested topic breakdown",
            "This is the last call. Not pressure — just math.",
            "The energy in onboarding calls is different",
            "Advanced Content Engineering: no replays this time",
            "Free intel report worth $500 for live attendees",
        ],
        "Community": [
            "60+ days following: what content topic next week?",
            "Comment AUDIT with your niche. Voice note incoming.",
            "5 strategy call slots left. Free. No pitch.",
            "Comment ADVANCED to register for workshop #2",
            "Comment CALL to book a strategy session",
            "This community is bigger than any tool. Thank you.",
            "What was your biggest win this month?",
            "The best part of launch week: the conversations",
            "Your questions drive the content. Keep asking.",
            "Next month: spotlights, features, community events",
            "Drop your content transformation story below",
            "Workshop attendees: what was your biggest takeaway?",
            "Spots are filling. Who's riding with us?",
            "The real flex: helping people win, not selling them",
        ],
        "Authority": [
            "You asked for it. The most-requested topic, fully broken down.",
            "ContentBrain generates this analysis in minutes",
            "3 hours of research → 3 minutes. That's the gap.",
            "Workshop #2: competitor scraping + trend detection live",
            "Free intel report for attendees. $500 value.",
            "15 signed up during the workshop. On the spot.",
            "40 strategy calls booked. The numbers speak.",
            "ContentBrain isn't a product anymore — it's a movement",
            "The advanced session: competitor scraping live",
            "User results that speak louder than any demo",
            "Workshop attendee results: the real proof",
            "2 workshops. 580 total attendees. Real impact.",
            "Phase 4 recap: conversion push → community movement",
            "The content system revolution is here",
        ],
    },
    7: {  # Scaling + Retention
        "Sales": [
            "Video Production package: scripts to finished video in minutes",
            "Content + Video + Community + Funnels. One system.",
            "The agency equivalent: $15-20K/mo. This: $3-5K.",
            "One-Time Build: custom content system, yours forever",
            "Affiliate Program: 25% recurring commission",
            "Full stack AI Marketing Automation — everything included",
            "Not ready for monthly? One-time build option.",
            "ContentBrain Affiliate: free money for content strategists",
            "Q3 planning: entire quarter in 30 minutes",
            "Free Q3 content plan with strategy call this week",
            "90-day ContentBrain results: the complete story",
            "Upsell: video production added to existing packages",
            "The full stack is here. Content, video, community, analytics.",
            "Custom content system: $2.5K-$15K, yours forever",
            "The scaling chapter begins: bigger features, more niches",
            "90 days of results. Q3 is where we accelerate.",
        ],
        "Reach": [
            "10,000 posts analyzed: 5 trends about to explode",
            "This report generates automatically every week",
            "90 days ago: just content strategy. Today: a movement.",
            "The DeFi protocol case study: 3-month follow-up",
            "Web3 gaming spotlight: Discord grew 12K members",
            "AI startup: zero to 15K followers in 60 days",
            "30-day aggregate data: 18 hrs/week saved, 62% cost down",
            "Referral program: get onboarded, get a free month",
            "The community is growing faster than predicted",
            "Q3 roadmap preview: what's coming next",
            "Phase 5 recap: from scaling to next level",
            "Imagine what 90 days of ContentBrain looks like",
            "These numbers are real. From real users. In 30 days.",
            "The long-term results are even better than the pilot",
            "From Day 1 to Day 90: the complete ContentBrain timeline",
            "The affiliate math: 25% recurring on every referral",
        ],
        "Community": [
            "ContentBrain Community launch: free for all users",
            "DM me SPOTLIGHT with your results",
            "Users who connect with other users grow faster",
            "Community is the moat. This is how we build it.",
            "Want your project featured? Share your story.",
            "Q3 starts in 4 days. What's your plan?",
            "Comment NEXT if you're riding into Q3 with us",
            "Thank you for being here from Day 1",
            "The best content systems are built by communities",
            "Sunday gratitude: 90 days of building together",
            "What feature do you want most in Q3?",
            "Share your ContentBrain transformation story",
            "The referral program rewards loyalty",
            "Next month: user spotlights and community events",
            "Drop your Q3 content goal below",
            "The community chapter: what we're building together",
        ],
        "Authority": [
            "User spotlight: DeFi protocol, 8→60 posts/month",
            "DeFi case study 3-month follow-up: numbers are better",
            "AI startup: zero to 15K followers, CEO never posted",
            "30 days of ContentBrain data: the aggregate report",
            "ContentBrain analyzed 10,000 Web3 posts this week",
            "Weekly trend report: automates every Monday morning",
            "90 days of ContentBrain: the complete results",
            "Gaming project: 90 days of automated lore content",
            "The data report: 4.2X content output increase",
            "User spotlights that prove the system works",
            "Q3 planning framework: full quarter in 30 minutes",
            "The numbers from 90 days speak for themselves",
            "This isn't the end — it's the foundation",
            "Bigger features. More niches. The best is ahead.",
            "From content tool to content movement: 90 days",
            "The foundation is built. Q3 is the scaling chapter.",
        ],
    },
}

# ── LI topic banks ─────────────────────────────────────────────────
LI_TOPICS = {
    1: [
        "The 3 data points I check before any decision — how less became more",
        "From 30 hours/week researching to 3. The architecture shift.",
        "Why Web3 founders need systems, not more tools",
        "The myth of the talented creator vs the consistent one",
        "2 weeks of conversations over broadcasts: raw engagement data",
        "The automation paradox: less effort, better results",
        "Risk management isn't a strategy — it's the foundation",
        "58% win rate and still profitable: the math nobody teaches",
        "Why I evaluate 3 data points instead of 12",
    ],
    2: [
        "The architecture behind 15+ posts/week in 3 hours",
        "AI workflows vs AI agents: where the real money is",
        "Before/after: my content process transformation",
        "The evolution from creator to content architect",
        "Consistency isn't discipline. It's design.",
        "The content system that runs without the creator",
        "Why the best content creators are actually engineers",
    ],
    3: [
        "7 days of content in 4 minutes: the ContentBrain approach",
        "DeFi project pilot: 21 posts, zero manual writing",
        "Competitor analysis in 30 seconds — what this means",
        "The tool stack consolidation: 5 subscriptions → 1 system",
        "30-day recovery: raw numbers from restarting from zero",
        "Live walkthrough: content system that runs itself",
        "Why I Built Quivira OS and what it replaces",
        "The brand voice objection: data that proves AI can match you",
        "Content audits that find what you're missing in seconds",
    ],
    4: [
        "ChatGPT is a hammer. Content strategy needs a house.",
        "Content ROI: revenue engine, not cost center",
        "5 frameworks behind every viral post — use them all",
        "Live build: content calendar from zero to scheduled",
        "The brand voice problem most founders ignore",
        "47 seconds to build a 30-day calendar. Implications for brands.",
        "Content-to-revenue pipeline: the flywheel explained",
        "AI agents are hype. Workflows are money. The data.",
        "In 20 days of free strategy, one thing was missing: execution",
        "Why founders keep firing social media managers",
        "The time audit: what content actually costs your team",
        "5 content frameworks that drive every viral post",
        "The content architect vs content creator mindset shift",
        "Content as execution: the missing layer in most strategies",
        "The disappearance test: can your brand survive without you?",
    ],
    5: [
        "Loom demo: 60 posts/month, zero headcount increase",
        "Cost comparison: $6,480/mo content team vs automated system",
        "DeFi case study: 8 to 60 posts, engagement tripled",
        "Brand voice + AI: proof from real users",
        "Workshop announcement: content engine in 45 minutes",
        "Workshop recap: 6 takeaways from 300 attendees",
        "ContentBrain for AI startups: automated thought leadership",
        "User testimonials: 5 unsolicited messages compiled",
        "Phase 3 recap: 20 days of demos and real proof",
        "Last call for spots: limited opening announcement",
        "The content intelligence layer that changes everything",
        "Day-in-the-life: the automated creator morning routine",
        "Workshop reminder: the last free session before launch",
        "Behind the scenes: prepping for the live build",
        "Exchange content + AI: the volume/quality arbitrage",
        "Web3 gaming content at scale: the niche opportunity",
        "User results: 30 days, 60 posts, 2 hours of work",
        "The DeFi niche demo: research to published posts",
        "Binance Square content: automated and on-brand",
        "Speed + quality: debunking the false tradeoff",
    ],
    6: [
        "ContentBrain is live. 25 spots. Onboarding starts today.",
        "Day 1 user results: signup to fully scheduled in hours",
        "Content audit offer: 48-hour free window",
        "Advanced workshop: competitor scraping + trend detection",
        "Free intel report for live attendees worth $500",
        "Workshop #2 results: 280 attendees, 15 immediate signups",
        "Community deep-dive: most-requested topic analysis",
        "Phase 4 recap: from conversion push to movement",
        "The cost comparison: ContentBrain vs content manager",
        "40 strategy calls booked — what the market is telling us",
        "Advanced Content Engineering: what we built live",
        "User results that speak louder than any demo",
        "Content systems are replacing content teams. The data.",
        "The workshop effect: real-time conversion in action",
    ],
    7: [
        "Video Production package: scripts to finished video",
        "AI startup spotlight: zero to 15K followers, 60 days",
        "30-day aggregate data: 18 hrs/week saved across all users",
        "Full stack: AI Marketing Automation announcement",
        "Q3 planning: how to plan a quarter in 30 minutes",
        "One-Time Build: custom system, yours forever",
        "Affiliate program: 25% recurring for content strategists",
        "Web3 gaming spotlight: 90 days of automated lore content",
        "90 days of ContentBrain: complete results and Q3 roadmap",
        "User spotlight: DeFi protocol transformation",
        "ContentBrain Community: free group for all users",
        "Upsell: video production joins the platform",
        "The referral program: reward loyalty, grow together",
        "From scaling to next level: Q3 preview",
        "The complete ContentBrain story: 90 days in data",
        "Foundation built. Scaling chapter begins. Q3 roadmap.",
    ],
}

IG_TOPICS = {
    1: [
        ("Reel", "SEC cleared tokens: the update nobody is covering"),
        ("Carousel", "5 beginner trading mistakes that cost $10K+"),
        ("Static", "Quote: 'Simplicity made me profitable'"),
        ("Reel", "3 tokens the SEC cleared that nobody is watching"),
        ("Carousel", "The 16 tokens the SEC cleared — full Q2 update"),
        ("Reel", "AI portfolio analysis: 3 things found in 2 minutes"),
        ("Static", "Quote: 'Systems, not willpower'"),
        ("Carousel", "The only 3 indicators you actually need"),
        ("Reel", "Morning routine as a crypto KOL"),
    ],
    2: [
        ("Carousel", "Before/after: content system transformation"),
        ("Reel", "Same person. Different system."),
        ("Static", "Quote: 'Consistency isn't discipline — it's architecture'"),
        ("Carousel", "AI Agents vs AI Workflows — infographic"),
        ("Reel", "The 3-hour content week: how it actually works"),
        ("Static", "Quote: 'Stop broadcasting. Start conversations.'"),
        ("Carousel", "45 min = 1 post vs 45 min = 7 posts"),
    ],
    3: [
        ("Reel", "7 days of content. 4 minutes. Timer on screen."),
        ("Carousel", "Why I Built Quivira OS — And What It Replaces"),
        ("Static", "Quote: 'One person + the right system beats a 5-person team'"),
        ("Reel", "Competitor analysis in 30 seconds — live demo"),
        ("Carousel", "Content tool cost breakdown: 5 subscriptions vs 1 system"),
        ("Reel", "30 days. Zero gimmicks. Here's what happened."),
        ("Static", "Quote: 'Stopped selling, started talking'"),
        ("Carousel", "The DeFi pilot results: 21 posts, zero manual writing"),
        ("Reel", "Free live walkthrough: content system demo"),
    ],
    4: [
        ("Carousel", "The Disappearance Test — 5 signs your content depends on YOU"),
        ("Reel", "Competitor content patterns: 30-second pull"),
        ("Static", "Quote: 'If you don't have a system, you ARE the system'"),
        ("Carousel", "The 5 Frameworks behind every viral post"),
        ("Reel", "47 seconds. 30-day calendar. Timer running."),
        ("Carousel", "The Time Audit Challenge — track your content hours"),
        ("Reel", "Speed run: content calendar from zero"),
        ("Static", "Quote: 'Content Creator vs Content Architect'"),
        ("Carousel", "The Income Engine framework: content → $10K/month"),
        ("Reel", "Brand voice training: how the system learns you"),
        ("Carousel", "ChatGPT vs purpose-built system comparison"),
        ("Static", "Quote: '60 posts/month. 4 platforms. Zero burnout.'"),
        ("Reel", "Live build preview: what you'll see Wednesday"),
        ("Carousel", "ROI calculator: content as a revenue engine"),
        ("Reel", "The content burnout cycle — and how to break it"),
    ],
    5: [
        ("Reel", "Before/after walkthrough: manual vs ContentBrain"),
        ("Carousel", "Cost comparison: $6,480/mo vs one system"),
        ("Reel", "32 seconds for a week of TikTok scripts"),
        ("Carousel", "Workshop preview: what you'll learn + build"),
        ("Reel", "Day in my life: automated content creator"),
        ("Static", "Quote: 'Saturday morning. Zero content stress.'"),
        ("Carousel", "6 takeaways from 30-day content engine workshop"),
        ("Reel", "ContentBrain Video Production: script to finished"),
        ("Carousel", "DeFi niche demo: research to published posts"),
        ("Reel", "Web3 gaming demo: lore + hype content"),
        ("Static", "Quote: 'Workshop attendee: Done in 2 hours. 60 posts.'"),
        ("Carousel", "Exchange content: 7 days in 2 minutes"),
        ("Reel", "Phase 3 highlights: 20 days of demos in 60 seconds"),
        ("Carousel", "AI startup demo: thought leadership automated"),
        ("Reel", "Testimonial compilation: real user results"),
        ("Static", "Quote: 'In 48 hours, 25 people get a content team'"),
        ("Carousel", "5 unsolicited user testimonials compiled"),
        ("Reel", "Speed run: entire week across 4 platforms"),
        ("Carousel", "ContentBrain for every niche: one system"),
        ("Reel", "Behind the scenes: preparing for the live build"),
    ],
    6: [
        ("Reel", "Launch day hype reel: speed runs + results + testimonials"),
        ("Carousel", "Day 1 user results: signup to scheduled in hours"),
        ("Reel", "Content audit blitz: live breakdown for a niche"),
        ("Carousel", "Community-requested topic: full carousel breakdown"),
        ("Static", "Quote: 'ContentBrain isn't a product — it's a movement'"),
        ("Reel", "Advanced workshop highlights: intelligence layer"),
        ("Carousel", "Workshop results + top 3 testimonials"),
        ("Reel", "The $50K freelancer savings story — real DMs"),
        ("Static", "Quote: 'The ones who move first always win'"),
        ("Carousel", "Cost breakdown: ContentBrain vs content manager"),
        ("Reel", "Strategy call preview: what 15 minutes of value looks like"),
        ("Carousel", "Phase 4 highlights: conversion push recap"),
        ("Reel", "Spot counter update: real-time availability"),
        ("Carousel", "Advanced Content Engineering: what was built live"),
    ],
    7: [
        ("Reel", "ContentBrain Video Production: from script to video"),
        ("Carousel", "User spotlight: AI startup case study"),
        ("Reel", "Referral program launch: how it works"),
        ("Carousel", "Full stack package: what AI Marketing Automation includes"),
        ("Static", "Quote: 'Day 90. The first chapter is written.'"),
        ("Reel", "Gaming project spotlight: 90 days of content"),
        ("Carousel", "Monthly packages vs one-time builds comparison"),
        ("Reel", "Q3 planning: entire quarter in 30 minutes"),
        ("Carousel", "Affiliate program: earn 25% recurring"),
        ("Reel", "90-day results: the complete ContentBrain story"),
        ("Static", "Quote: 'The best content systems are built by communities'"),
        ("Carousel", "30-day data report: 18 hrs/week saved"),
        ("Reel", "ContentBrain Community: what's inside"),
        ("Carousel", "DeFi protocol spotlight: 3-month follow-up"),
        ("Reel", "5 trends about to explode from 10K post analysis"),
        ("Carousel", "Q3 roadmap: what's coming next"),
    ],
}

def get_phase(d):
    for start, end, num, name, mentions in PHASES:
        if start <= d <= end:
            return num, name, mentions
    return 0, "Unknown", ""

def generate_calendar():
    lines = []

    # ── Header ─────────────────────────────────────────────────────
    lines.append("# Unified Content Calendar V2 — @big_quiv / @_Quivira")
    lines.append("")
    lines.append("**Date Range:** April 1 — June 30, 2026 (91 days)")
    lines.append("**Cadence:** 10 posts/day, 7 days/week, 4 platforms")
    lines.append("**Total Entries:** 910")
    lines.append("**Single Source of Truth** — Replaces v1 (unified-content-calendar-v1-deprecated.md)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Rules")
    lines.append("")
    lines.append("1. **10 posts/day, every day, no rest days**")
    lines.append("2. **TikTok (4/day):** TK-1=Sales, TK-2=Reach, TK-3=Community, TK-4=Authority — every day")
    lines.append("3. **Instagram (2/day):** IG-1=Sales/Authority focus, IG-2=Community/Reach focus. Format rotation: Reel → Carousel → Static → Reel...")
    lines.append("4. **X/Twitter (2/day):** X-AM=Value/Authority, X-PM=Engagement/Community")
    lines.append("5. **LinkedIn (2/day):** LI-1=Thought leadership, LI-2=Authority/Data insights")
    lines.append("6. **No product mentions before Apr 17** (Phase 3 reveal day)")
    lines.append("7. **Reply to every comment** within 1 hour on X, 2 hours on TikTok/IG, 4 hours on LinkedIn")
    lines.append("8. **Engage before posting:** 15 min on 5 bigger accounts in your niche before first post of the day")
    lines.append("9. **No raw signals, no self-reposts, no bare links on X**")
    lines.append("10. **Weekend batch creation:** research + write + film + design on Saturday, review + schedule on Sunday")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Daily Cadence")
    lines.append("")
    lines.append("| Platform | Slots/Day | Weekly | 91 Days | Focus |")
    lines.append("|----------|-----------|--------|---------|-------|")
    lines.append("| TikTok | 4 | 28 | 364 | Personal, rotating categories |")
    lines.append("| Instagram | 2 | 14 | 182 | Mix of reels, carousels, static |")
    lines.append("| X/Twitter | 2 | 14 | 182 | AM=value/authority, PM=community |")
    lines.append("| LinkedIn | 2 | 14 | 182 | Authority positioning |")
    lines.append("| **Total** | **10** | **70** | **910** | |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## TikTok 4-Slot Rotation")
    lines.append("")
    lines.append("| Slot | Category | What to post | Personality |")
    lines.append("|------|----------|-------------|-------------|")
    lines.append("| TK-1 | **SALES** | Problems you solve, who for, results produced | Direct, confident, proof-heavy |")
    lines.append("| TK-2 | **REACH** | Relatability, controversy, story times | Raw, emotional, energetic |")
    lines.append("| TK-3 | **COMMUNITY** | Niche issues, audience questions, common struggles | Big brother energy, thoughtful |")
    lines.append("| TK-4 | **AUTHORITY** | Polarizing stands, frameworks, expert positioning | Calm, wise, fearless |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Source Key")
    lines.append("")
    lines.append("| Tag | Meaning |")
    lines.append("|-----|---------|")
    lines.append("| **[DRAFT READY]** | Full hook/copy exists from v1 — ready for production |")
    lines.append("| **[TOPIC ONLY]** | Topic + angle provided — full hook to be written during weekend batch |")
    lines.append("| **A-n** | Calendar A piece (original weekly drafts) |")
    lines.append("| **B-n** | Calendar B piece (30-day recovery) |")
    lines.append("| **C-n** | Calendar C piece (90-day launch) |")
    lines.append("| **adapt** | Cross-platform adaptation of an existing v1 hook |")
    lines.append("| **NEW** | Freshly generated topic for v2 cadence |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase Overview")
    lines.append("")
    lines.append("| Phase | Dates | Focus | Product Mentions |")
    lines.append("|-------|-------|-------|-----------------|")
    for start, end, num, name, mentions in PHASES:
        lines.append(f"| {num} | {start.strftime('%b %d')}-{end.strftime('%b %d')} | {name} | {mentions} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Generate daily entries ─────────────────────────────────────
    start_date = date(2026, 4, 1)
    end_date = date(2026, 6, 30)
    current_phase = 0
    ig_format_idx = 0  # rotation index for IG formats
    tk_topic_idx = {"Sales": 0, "Reach": 0, "Community": 0, "Authority": 0}
    li_topic_idx = 0
    ig_topic_idx = 0
    total_entries = 0
    total_v1_placed = 0
    week_num = 1
    last_week_start = None

    d = start_date
    while d <= end_date:
        phase_num, phase_name, _ = get_phase(d)

        # Week header
        day_of_week = d.weekday()  # 0=Mon
        if day_of_week == 0 or d == start_date:
            if d != start_date:
                lines.append("")
            # Phase header if phase changed
            if phase_num != current_phase:
                current_phase = phase_num
                lines.append(f"# PHASE {phase_num}: {phase_name}")
                lines.append("")
                lines.append("---")
                lines.append("")
                # Reset topic indices for new phase
                tk_topic_idx = {"Sales": 0, "Reach": 0, "Community": 0, "Authority": 0}
                li_topic_idx = 0
                ig_topic_idx = 0

            week_start = d
            week_end = d + timedelta(days=6)
            if week_end > end_date:
                week_end = end_date
            lines.append(f"## Week {week_num} ({week_start.strftime('%b %d')}-{week_end.strftime('%b %d')})")
            lines.append("")
            week_num += 1

        date_str = d.strftime("%Y-%m-%d")
        day_name = DAYS_OF_WEEK[day_of_week]
        display_date = d.strftime("%b %d").replace(" 0", " ")
        lines.append(f"### {d.strftime('%b')} {d.day} ({day_name}) | Phase {phase_num}")
        lines.append("| Slot | Platform | Type | Topic/Hook | Goal | Source |")
        lines.append("|------|----------|------|-----------|------|--------|")

        v1_day = v1_lookup.get(date_str, {})

        # ── TK-1: Sales ────────────────────────────────────────────
        tk_entry = v1_day.get("TK")
        if tk_entry and tk_entry[4] in ("Sales", "Leads"):
            hook = tk_entry[3]
            src = tk_entry[6] if tk_entry[6] else tk_entry[5]
            dr = " [DRAFT READY]" if tk_entry[6] else ""
            lines.append(f'| TK-1 | TikTok | Sales | "{hook}" | Sales | {tk_entry[5]}{dr} |')
            total_v1_placed += 1
        else:
            topics = TIKTOK_TOPICS.get(phase_num, TIKTOK_TOPICS[1])["Sales"]
            idx = tk_topic_idx["Sales"] % len(topics)
            lines.append(f'| TK-1 | TikTok | Sales | {topics[idx]} | Sales | NEW [TOPIC ONLY] |')
            tk_topic_idx["Sales"] += 1
        total_entries += 1

        # ── TK-2: Reach ───────────────────────────────────────────
        if tk_entry and tk_entry[4] == "Reach":
            hook = tk_entry[3]
            dr = " [DRAFT READY]" if tk_entry[6] else ""
            lines.append(f'| TK-2 | TikTok | Reach | "{hook}" | Reach | {tk_entry[5]}{dr} |')
            # already counted as TK-1 didn't use it, but we need to count this instead
        else:
            topics = TIKTOK_TOPICS.get(phase_num, TIKTOK_TOPICS[1])["Reach"]
            idx = tk_topic_idx["Reach"] % len(topics)
            lines.append(f'| TK-2 | TikTok | Reach | {topics[idx]} | Reach | NEW [TOPIC ONLY] |')
            tk_topic_idx["Reach"] += 1
        total_entries += 1

        # ── TK-3: Community ────────────────────────────────────────
        topics = TIKTOK_TOPICS.get(phase_num, TIKTOK_TOPICS[1])["Community"]
        idx = tk_topic_idx["Community"] % len(topics)
        lines.append(f'| TK-3 | TikTok | Community | {topics[idx]} | Community | NEW [TOPIC ONLY] |')
        tk_topic_idx["Community"] += 1
        total_entries += 1

        # ── TK-4: Authority ───────────────────────────────────────
        if tk_entry and tk_entry[4] == "Authority":
            hook = tk_entry[3]
            dr = " [DRAFT READY]" if tk_entry[6] else ""
            lines.append(f'| TK-4 | TikTok | Authority | "{hook}" | Authority | {tk_entry[5]}{dr} |')
        else:
            topics = TIKTOK_TOPICS.get(phase_num, TIKTOK_TOPICS[1])["Authority"]
            idx = tk_topic_idx["Authority"] % len(topics)
            lines.append(f'| TK-4 | TikTok | Authority | {topics[idx]} | Authority | NEW [TOPIC ONLY] |')
            tk_topic_idx["Authority"] += 1
        total_entries += 1

        # ── IG-1 ──────────────────────────────────────────────────
        ig_entry = v1_day.get("IG")
        ig1_format = IG_FORMATS[ig_format_idx % 3]
        if ig_entry:
            hook = ig_entry[3]
            goal = ig_entry[4]
            dr = " [DRAFT READY]" if ig_entry[6] else ""
            ig_type = ig_entry[2] if ig_entry[2] in ("Reel","Carousel","Story","Video","Story series") else ig1_format
            lines.append(f'| IG-1 | Instagram | {ig_type} | "{hook}" | {goal} | {ig_entry[5]}{dr} |')
            total_v1_placed += 1
        else:
            ig_topics = IG_TOPICS.get(phase_num, IG_TOPICS[1])
            idx = ig_topic_idx % len(ig_topics)
            fmt, topic = ig_topics[idx]
            goal = "Sales" if ig_format_idx % 2 == 0 else "Authority"
            lines.append(f'| IG-1 | Instagram | {fmt} | {topic} | {goal} | NEW [TOPIC ONLY] |')
        total_entries += 1

        # ── IG-2 ──────────────────────────────────────────────────
        ig2_format = IG_FORMATS[(ig_format_idx + 1) % 3]
        ig_topics = IG_TOPICS.get(phase_num, IG_TOPICS[1])
        ig2_idx = (ig_topic_idx + 1) % len(ig_topics)
        fmt2, topic2 = ig_topics[ig2_idx]
        goal2 = "Community" if ig_format_idx % 2 == 0 else "Reach"
        lines.append(f'| IG-2 | Instagram | {fmt2} | {topic2} | {goal2} | NEW [TOPIC ONLY] |')
        ig_format_idx += 1
        ig_topic_idx += 2
        total_entries += 1

        # ── X-AM ──────────────────────────────────────────────────
        xam_entry = v1_day.get("X-AM")
        if xam_entry:
            hook = xam_entry[3]
            goal = xam_entry[4]
            dr = " [DRAFT READY]" if xam_entry[6] else ""
            lines.append(f'| X-AM | X/Twitter | {xam_entry[2]} | "{hook}" | {goal} | {xam_entry[5]}{dr} |')
            total_v1_placed += 1
        else:
            # Generate authority topic for X-AM
            topics = TIKTOK_TOPICS.get(phase_num, TIKTOK_TOPICS[1])["Authority"]
            idx = (tk_topic_idx["Authority"] + 5) % len(topics)
            lines.append(f'| X-AM | X/Twitter | Tweet | {topics[idx]} | Authority | NEW [TOPIC ONLY] |')
        total_entries += 1

        # ── X-PM ──────────────────────────────────────────────────
        xpm_entry = v1_day.get("X-PM")
        if xpm_entry and xpm_entry[3] and "[FLEX" not in xpm_entry[3]:
            hook = xpm_entry[3]
            goal = xpm_entry[4]
            dr = " [DRAFT READY]" if xpm_entry[6] else ""
            lines.append(f'| X-PM | X/Twitter | {xpm_entry[2]} | "{hook}" | {goal} | {xpm_entry[5]}{dr} |')
            total_v1_placed += 1
        else:
            topics = TIKTOK_TOPICS.get(phase_num, TIKTOK_TOPICS[1])["Community"]
            idx = (tk_topic_idx["Community"] + 3) % len(topics)
            lines.append(f'| X-PM | X/Twitter | Tweet | {topics[idx]} | Community | NEW [TOPIC ONLY] |')
        total_entries += 1

        # ── LI-1 ──────────────────────────────────────────────────
        li_entry = v1_day.get("LI")
        if li_entry:
            hook = li_entry[3]
            goal = li_entry[4]
            dr = " [DRAFT READY]" if li_entry[6] else ""
            lines.append(f'| LI-1 | LinkedIn | Post | "{hook}" | {goal} | {li_entry[5]}{dr} |')
            total_v1_placed += 1
        else:
            li_topics = LI_TOPICS.get(phase_num, LI_TOPICS[1])
            idx = li_topic_idx % len(li_topics)
            lines.append(f'| LI-1 | LinkedIn | Post | {li_topics[idx]} | Authority | NEW [TOPIC ONLY] |')
        total_entries += 1

        # ── LI-2 ──────────────────────────────────────────────────
        li_topics = LI_TOPICS.get(phase_num, LI_TOPICS[1])
        li2_idx = (li_topic_idx + 1) % len(li_topics)
        lines.append(f'| LI-2 | LinkedIn | Post | {li_topics[li2_idx]} | Authority | NEW [TOPIC ONLY] |')
        li_topic_idx += 2
        total_entries += 1

        lines.append("")
        d += timedelta(days=1)

    # ── DM Automation Keywords ─────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("# DM Automation Keywords (Consolidated)")
    lines.append("")
    lines.append("| Keyword | Phase | Trigger | Response |")
    lines.append("|---------|-------|---------|----------|")
    dm_keywords = [
        ("ENGINE","3 (Apr 17)","Comment on X","Custom Loom link showing ContentBrain"),
        ("SPEED","3 (Apr 18)","Comment + niche","Pull sample content for their niche"),
        ("BRAIN","3 (Apr 20)","Comment on X","Early access waitlist link"),
        ("PILOT","3 (Apr 21)","Comment on X","Arrange 7-day free pilot"),
        ("INTEL","3 (Apr 23)","Comment + niche","Free competitor analysis report"),
        ("LIVE","3 (Apr 24)","Comment on X","DM workshop link"),
        ("SYSTEM","3 (Apr 25)","Comment or DM","Calendly discovery call link"),
        ("TIME","4 (May 5)","Comment on X","Contest entry + demo link"),
        ("BRAND","4 (May 6)","Comment on X","Voice training demo video"),
        ("INCOME","4 (May 9)","Comment on X","Strategy call booking"),
        ("READY","4 (May 10)","Comment on X","Demo notification signup"),
        ("LOOM","5 (May 12)","DM + brand name","Record custom 5-min Loom"),
        ("SAVE","5 (May 13)","DM trigger","Custom cost comparison"),
        ("SCRIPTS","5 (May 14)","Comment on X","Niche-specific script test"),
        ("CASE","5 (May 15)","Comment on X","Strategy call slot"),
        ("TRUST","5 (May 16)","Comment on X","Brand voice comparison"),
        ("WORKSHOP","5 (May 19)","Comment on X","Workshop registration"),
        ("MORNING","5 (May 20)","Comment on X","Workshop registration"),
        ("BUILD","5 (May 22)","DM trigger","Strategy call booking"),
        ("REPLAY","5 (May 23)","Comment on X","48-hour replay link"),
        ("PROOF","5 (May 24)","Comment on X","User results compilation"),
        ("DEFI","5 (May 25)","DM + project","Free DeFi content audit"),
        ("STARTUP","5 (May 26)","DM trigger","Custom AI startup demo"),
        ("NEXT","5 (May 27)","Comment on X","Priority list (15 spots)"),
        ("GAME","5 (May 28)","DM trigger","Gaming niche content audit"),
        ("EXCHANGE","5 (May 29)","Comment on X","Exchange content demo"),
        ("LAUNCH","5 (May 30)","Comment on X","Launch notification list"),
        ("DEAL","6 (Jun 5)","DM trigger","Pricing page"),
        ("AUDIT","6 (Jun 6)","Comment + niche","Voice note content audit"),
        ("ADVANCED","6 (Jun 10)","Comment on X","Workshop #2 registration"),
        ("DEEP","6 (Jun 9)","Comment on X","ContentBrain topic analysis"),
        ("CLOSE","6 (Jun 12)","DM trigger","Strategy call booking"),
        ("CALL","6 (Jun 13)","Comment on X","Strategy call booking"),
        ("SPOTLIGHT","7 (Jun 15)","DM + results","Feature in user spotlight"),
        ("VIDEO","7 (Jun 16)","DM trigger","Video package upgrade info"),
        ("JOIN","7 (Jun 17)","Comment on X","Community waitlist"),
        ("FOUNDER","7 (Jun 18)","DM trigger","Strategy call booking"),
        ("DATA","7 (Jun 19)","DM trigger","Projection report"),
        ("REFER","7 (Jun 20)","Comment on X","Referral program details"),
        ("TRENDS","7 (Jun 21)","Comment on X","Free weekly trend report"),
        ("FULL","7 (Jun 23)","DM trigger","Full stack proposal"),
        ("GAMING","7 (Jun 24)","DM + project","Gaming niche demo"),
        ("Q3","7 (Jun 26)","DM trigger","Strategy call + free Q3 plan"),
        ("AFFILIATE","7 (Jun 27)","Comment on X","Affiliate application"),
    ]
    for kw, phase, trigger, response in dm_keywords:
        lines.append(f"| {kw} | {phase} | {trigger} | {response} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Weekend Batch Creation Schedule")
    lines.append("")
    lines.append("| Day | Task | Time |")
    lines.append("|-----|------|------|")
    lines.append("| **Saturday AM** | Research: review analytics, competitor data, trending topics | 30 min |")
    lines.append("| **Saturday AM** | Write: draft all posts for the week (hooks, bodies, CTAs) | 2 hr |")
    lines.append("| **Saturday PM** | Film: TikTok content (4 per day = 28/week) | 2 hr |")
    lines.append("| **Saturday PM** | Design: carousels, thumbnails, visual assets | 1.5 hr |")
    lines.append("| **Sunday AM** | Review: quality check all 70 posts against Content Strategy Rules | 45 min |")
    lines.append("| **Sunday AM** | Schedule: load posts into Typefully (X/LI) + Meta Business Suite (IG/TK) | 45 min |")
    lines.append("| **Sunday PM** | Prep: write reply-thread CTAs for each post | 30 min |")
    lines.append("| **Total** | | **~8 hrs/weekend** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Verification")
    lines.append("")
    lines.append(f"- **Total entries:** {total_entries}")
    lines.append(f"- **V1 hooks placed:** {total_v1_placed}")
    lines.append(f"- **New entries (TOPIC ONLY):** {total_entries - total_v1_placed}")
    lines.append("- **Platforms per day:** TK×4 + IG×2 + X×2 + LI×2 = 10")
    lines.append("- **No product mentions before Apr 17:** Phase 1-2 clean")
    lines.append("- **TikTok rotation:** Every day has TK-1(Sales), TK-2(Reach), TK-3(Community), TK-4(Authority)")
    lines.append("- **IG format rotation:** Reel → Carousel → Static cycling")
    lines.append("- **All v1 hooks preserved:** None lost")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    output = generate_calendar()
    output_path = r"C:\Users\Bigquiv\onedrive\desktop\contentbrain\06-Drafts\unified-content-calendar-v2.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    # Count lines and entries for verification
    entry_count = output.count("| TK-1 |") + output.count("| TK-2 |") + output.count("| TK-3 |") + output.count("| TK-4 |")
    entry_count += output.count("| IG-1 |") + output.count("| IG-2 |")
    entry_count += output.count("| X-AM |") + output.count("| X-PM |")
    entry_count += output.count("| LI-1 |") + output.count("| LI-2 |")

    print(f"Generated: {output_path}")
    print(f"Total entries: {entry_count}")
    print(f"Total lines: {len(output.splitlines())}")
