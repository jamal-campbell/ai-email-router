#!/usr/bin/env python3
"""
Email Corpus Generator for AI Categorization Training
Generates realistic sample emails across multiple business categories.
"""

import json
import random
from datetime import datetime, timedelta

# Email categories for routing
CATEGORIES = {
    "support": "Technical Support",
    "sales": "Sales Inquiry",
    "billing": "Billing/Payments",
    "complaint": "Customer Complaint",
    "hr": "Human Resources",
    "it_helpdesk": "IT Help Desk",
    "partnership": "Partnership/Business Development",
    "legal": "Legal/Compliance",
    "general": "General Inquiry",
    "spam": "Spam/Marketing"
}

# Sample data for generating realistic emails
FIRST_NAMES = ["James", "Sarah", "Michael", "Emily", "David", "Jennifer", "Robert", "Lisa", "John", "Amanda",
               "William", "Jessica", "Christopher", "Ashley", "Daniel", "Michelle", "Matthew", "Stephanie",
               "Andrew", "Nicole", "Carlos", "Maria", "Wei", "Priya", "Mohammed", "Fatima"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
              "Martinez", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Lee", "Chen", "Patel",
              "Kim", "Singh", "Wong", "Kumar"]

COMPANIES = ["Acme Corp", "TechStart Inc", "Global Solutions", "Premier Services", "Innovate Labs",
             "DataFlow Systems", "CloudNine Tech", "Vertex Industries", "Apex Consulting", "Synergy Partners",
             "BlueSky Enterprises", "NextGen Software", "Quantum Analytics", "Elevate Digital", "PrimePath LLC"]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "company.com", "business.org",
           "enterprise.net", "corp.io", "tech.co", "solutions.com"]

# Email templates by category
EMAIL_TEMPLATES = {
    "support": [
        {
            "subject": "Unable to access my account",
            "body": """Hi Support Team,

I've been trying to log into my account for the past hour but keep getting an error message saying "Invalid credentials." I'm certain I'm using the correct password as I just reset it yesterday.

Can you please help me regain access to my account? My username is {username}.

Thank you for your assistance.

Best regards,
{name}"""
        },
        {
            "subject": "Software crashing on startup",
            "body": """Hello,

Since the latest update, the application crashes immediately upon startup. I've tried reinstalling but the issue persists.

System info:
- OS: Windows 11
- RAM: 16GB
- Version: 3.2.1

Please advise on how to resolve this issue.

Thanks,
{name}"""
        },
        {
            "subject": "Feature not working as expected",
            "body": """Dear Support,

The export to PDF feature is not working correctly. When I try to export my reports, the formatting is completely broken and images are missing.

I've attached screenshots showing the issue. This is urgent as I need to submit these reports by end of week.

Could someone look into this ASAP?

Regards,
{name}
{company}"""
        },
        {
            "subject": "Integration with third-party API failing",
            "body": """Hi there,

We're experiencing issues with the API integration. The webhook endpoints are returning 500 errors intermittently.

Error logs show: "Connection timeout after 30000ms"

This started happening around 2 days ago. Is there a known issue with the API servers?

Best,
{name}"""
        },
        {
            "subject": "Need help setting up automation",
            "body": """Hello Support Team,

I'm trying to set up automated workflows but I can't figure out how to configure the trigger conditions. The documentation mentions "event-based triggers" but I don't see that option in my dashboard.

Am I missing something? Could you provide step-by-step guidance?

Thank you,
{name}"""
        },
        {
            "subject": "Data sync issues between devices",
            "body": """Hi,

My data isn't syncing properly between my laptop and mobile app. Changes I make on one device don't appear on the other, even after waiting several hours.

I've tried logging out and back in on both devices but the problem continues.

Please help!

{name}"""
        },
        {
            "subject": "Error when uploading files",
            "body": """Support,

Every time I try to upload a file larger than 5MB, I get an error: "Upload failed. Please try again."

Smaller files work fine. Is there a file size limit I'm not aware of? My plan should allow up to 100MB uploads.

Thanks for looking into this.

{name}
Account ID: {account_id}"""
        },
        {
            "subject": "Cannot generate reports",
            "body": """Hello,

The reporting module seems to be broken. When I click "Generate Report," nothing happens - no loading indicator, no error message, just nothing.

I've cleared my browser cache and tried different browsers (Chrome, Firefox, Safari) with the same result.

This is blocking our weekly business review. Please prioritize.

Regards,
{name}"""
        }
    ],

    "sales": [
        {
            "subject": "Interested in your enterprise solution",
            "body": """Hello Sales Team,

I came across your product while researching solutions for our company's needs. We're a {size}-person organization looking to improve our workflow efficiency.

Could you provide more information about:
1. Enterprise pricing
2. Implementation timeline
3. Available integrations

Looking forward to hearing from you.

Best regards,
{name}
{title}
{company}"""
        },
        {
            "subject": "Request for product demo",
            "body": """Hi,

We're evaluating several vendors for our upcoming project and would like to schedule a demo of your platform.

Our team of {team_size} people would benefit from seeing:
- Core features walkthrough
- Customization options
- Security capabilities

Please let me know your availability for next week.

Thanks,
{name}"""
        },
        {
            "subject": "Pricing inquiry for annual subscription",
            "body": """Dear Sales,

We're currently on the monthly plan but considering switching to annual billing.

Questions:
1. What discount is available for annual commitment?
2. Can we add users mid-cycle?
3. Is there a volume discount for 50+ seats?

Appreciate a quick response as we're finalizing our budget.

{name}
{company}"""
        },
        {
            "subject": "Comparing your solution with competitors",
            "body": """Hello,

We're in the final stages of vendor selection and your product is on our shortlist alongside two competitors.

What differentiates your solution? Specifically interested in:
- Scalability
- Customer support quality
- Roadmap for future features

A call this week would be great if possible.

Regards,
{name}"""
        },
        {
            "subject": "Startup discount available?",
            "body": """Hi there,

We're an early-stage startup ({funding_stage}) and very interested in using your product. However, the standard pricing is a bit steep for our current budget.

Do you offer any startup programs or discounts for early-stage companies?

We have {employee_count} employees and expect to grow significantly this year.

Thanks for considering,
{name}
Founder, {company}"""
        },
        {
            "subject": "Need solution for remote team management",
            "body": """Sales Team,

Our company recently went fully remote and we're struggling with team coordination and project visibility.

We need a solution that can:
- Track project progress across time zones
- Integrate with Slack and Google Workspace
- Provide management dashboards

Budget is approximately ${budget}/month. Does your product fit these requirements?

Best,
{name}"""
        },
        {
            "subject": "Upgrading from free tier",
            "body": """Hello,

I've been using the free version for 3 months and I'm ready to upgrade. Before I do, I want to make sure I choose the right plan.

My needs:
- 10 team members
- API access
- Priority support

Which plan would you recommend?

Thanks,
{name}"""
        }
    ],

    "billing": [
        {
            "subject": "Unexpected charge on my account",
            "body": """Hello Billing Department,

I noticed an unexpected charge of ${amount} on my credit card statement dated {date}. I don't recognize this charge and would like clarification.

My account email: {email}
Last 4 digits of card: {card_last4}

Please investigate and get back to me.

Thank you,
{name}"""
        },
        {
            "subject": "Request for refund",
            "body": """Hi,

I'd like to request a refund for my recent purchase. I accidentally subscribed to the wrong plan and realized immediately after.

Order ID: {order_id}
Amount: ${amount}
Date: {date}

I haven't used any of the premium features. Please process the refund at your earliest convenience.

Regards,
{name}"""
        },
        {
            "subject": "Need invoice for tax purposes",
            "body": """Hello,

Could you please send me invoices for all payments made in {year}? I need them for my tax records.

Account email: {email}
Company name: {company}
Tax ID: {tax_id}

PDF format preferred.

Thank you,
{name}"""
        },
        {
            "subject": "Update payment method",
            "body": """Hi Billing,

My credit card on file is about to expire. How do I update my payment method? I can't seem to find the option in account settings.

Please advise before my next billing date on {date}.

Thanks,
{name}"""
        },
        {
            "subject": "Dispute charge - service not delivered",
            "body": """To Whom It May Concern,

I am disputing the charge of ${amount} made on {date}. Despite paying for the premium service, I never received access to the advertised features.

I contacted support multiple times (ticket numbers: {tickets}) but the issue was never resolved.

I expect a full refund within 5 business days or I will escalate this to my credit card company.

{name}"""
        },
        {
            "subject": "Question about prorated charges",
            "body": """Hello,

I upgraded my plan mid-cycle and I'm confused about the prorated charges on my bill.

The math doesn't seem right:
- Old plan: $29/month
- New plan: $79/month
- Days remaining: 15
- Charged: ${amount}

Can you break down how this was calculated?

Thanks,
{name}"""
        },
        {
            "subject": "Cancel subscription and confirm no future charges",
            "body": """Hi,

I would like to cancel my subscription effective immediately. Please confirm:
1. Cancellation has been processed
2. No future charges will be made
3. When my access will end

Account email: {email}

Thank you,
{name}"""
        },
        {
            "subject": "Payment failed notification - but payment went through",
            "body": """Hello,

I received an email saying my payment failed, but when I check my bank account, the charge went through successfully.

Transaction ID from my bank: {transaction_id}
Amount: ${amount}
Date: {date}

Please update my account status. I don't want to lose access due to this error.

{name}"""
        }
    ],

    "complaint": [
        {
            "subject": "Extremely disappointed with service quality",
            "body": """To Management,

I have been a customer for {years} years and I'm extremely disappointed with the recent decline in service quality.

Issues I've experienced:
1. Response times have increased from hours to days
2. Support agents seem undertrained
3. Features that used to work now have bugs

Unless things improve significantly, I will be taking my business elsewhere and sharing my experience on review sites.

Frustrated customer,
{name}
Account: {account_id}"""
        },
        {
            "subject": "Unacceptable downtime affecting our business",
            "body": """This is unacceptable.

Your service has been down for {hours} hours now. This is costing our business real money - we estimate losses of ${amount} so far.

We pay premium prices and expect premium reliability. This is the third major outage this quarter.

I demand:
1. Immediate resolution
2. Detailed post-mortem
3. Service credits

{name}
{title}, {company}"""
        },
        {
            "subject": "Misleading advertising - product doesn't match claims",
            "body": """Hello,

I purchased your product based on claims made on your website and marketing materials. The actual product does NOT deliver on these promises.

Specific discrepancies:
- Claimed "99.9% uptime" - actual uptime has been around 95%
- Advertised "unlimited storage" - discovered there's a hidden 50GB cap
- Promised "24/7 support" - support is only available business hours

This feels like false advertising. I want a full refund and an explanation.

{name}"""
        },
        {
            "subject": "Data loss due to your system error",
            "body": """URGENT - CRITICAL ISSUE

Due to what appears to be a bug in your system, I have lost {months} months of data. This data is IRREPLACEABLE and critical to my business.

What happened:
1. I clicked "Save" as usual
2. Got an error message
3. When I refreshed, all my data was gone

I need immediate escalation to your engineering team. This needs to be resolved TODAY.

{name}
Phone: {phone}"""
        },
        {
            "subject": "Rude customer service representative",
            "body": """I need to file a formal complaint about my interaction with one of your support representatives.

Date: {date}
Time: {time}
Rep name/ID: {rep_name}

The representative was dismissive, condescending, and eventually hung up on me before my issue was resolved.

I have the call recorded and am prepared to share it. This behavior is completely unprofessional.

Please have a manager contact me.

{name}
{phone}"""
        },
        {
            "subject": "Bait and switch on pricing",
            "body": """Hello,

I signed up based on the pricing shown on your website: ${original_price}/month. After entering my payment details, I was charged ${actual_price}/month.

When I contacted support, they said the website pricing was "outdated." This is classic bait and switch tactics.

I want the price I was promised or I'm reporting this to consumer protection agencies.

{name}"""
        }
    ],

    "hr": [
        {
            "subject": "PTO request for upcoming vacation",
            "body": """Hi HR Team,

I would like to request PTO for the following dates:
- Start: {start_date}
- End: {end_date}
- Total days: {days}

I have {balance} days remaining in my balance. My manager {manager} has been notified.

Please confirm approval.

Thanks,
{name}
{department}"""
        },
        {
            "subject": "Question about health benefits enrollment",
            "body": """Hello,

Open enrollment is coming up and I have questions about our health insurance options:

1. What's the difference between the PPO and HDHP plans?
2. Can I add my domestic partner?
3. When do changes take effect?

Could we schedule a brief call to discuss?

Thanks,
{name}"""
        },
        {
            "subject": "Reporting workplace concern",
            "body": """Dear HR,

I need to report a concern about workplace behavior. I would prefer to discuss this in person and in confidence.

Without going into details in email, it involves inappropriate comments made by a colleague that have made me uncomfortable.

Please let me know when we can meet privately.

{name}
{department}"""
        },
        {
            "subject": "Remote work policy clarification",
            "body": """Hi HR,

I'd like clarification on our remote work policy. Specifically:

1. How many days per week can we work remotely?
2. Do we need approval for each remote day?
3. Are there core hours we must be available?
4. What equipment is provided for home office?

I want to make sure I'm compliant with company policy.

Thanks,
{name}"""
        },
        {
            "subject": "Salary review request",
            "body": """Dear HR,

I would like to formally request a salary review. I have been in my current role for {years} years and believe my compensation no longer reflects my contributions and market rates.

Key points:
- Successfully led {projects} major projects
- Expanded responsibilities beyond original job description
- Industry salary data shows I'm below market rate

I'd appreciate the opportunity to discuss this.

Best regards,
{name}
{title}"""
        },
        {
            "subject": "Parental leave information needed",
            "body": """Hello HR Team,

My spouse and I are expecting a child in {months} months. I need information about our parental leave policy:

1. How much paid leave is available?
2. How far in advance should I apply?
3. Can leave be taken intermittently?
4. What documentation is required?

Thank you,
{name}"""
        },
        {
            "subject": "Exit interview scheduling",
            "body": """Hi,

As you know, my last day is {date}. I'd like to schedule my exit interview and discuss the offboarding process.

I also have questions about:
- 401(k) rollover options
- COBRA coverage
- Final paycheck timing
- Returning equipment

Please let me know available times.

{name}"""
        }
    ],

    "it_helpdesk": [
        {
            "subject": "Password reset needed",
            "body": """Hi IT,

I've been locked out of my account after too many failed password attempts. I need a password reset ASAP as I have an important client meeting in {hours} hour(s).

Username: {username}
Employee ID: {employee_id}

Please call me when reset is done: {phone}

Thanks,
{name}"""
        },
        {
            "subject": "New laptop setup request",
            "body": """Hello IT Team,

I'm a new employee starting on {date} in the {department} department. My manager {manager} mentioned I should reach out about getting my laptop and accounts set up.

I'll need:
- Laptop (MacBook preferred if available)
- Email account
- Access to {systems}
- VPN setup

Please let me know what information you need from me.

Thanks,
{name}"""
        },
        {
            "subject": "VPN connection issues from home",
            "body": """IT Support,

I can't connect to the VPN from home. I keep getting error: "Connection attempt failed - Server not responding"

What I've tried:
- Restarting the VPN client
- Restarting my computer
- Checking my internet connection (it's fine)

I need VPN access for an important deadline today.

{name}
{department}"""
        },
        {
            "subject": "Software installation request",
            "body": """Hi IT,

I need the following software installed on my workstation for a new project:

1. {software1} (latest version)
2. {software2}
3. {software3}

My manager has approved this request. Let me know if you need formal approval documentation.

Computer name: {computer_name}
Location: {office_location}

Thanks,
{name}"""
        },
        {
            "subject": "Suspicious email received - possible phishing",
            "body": """IT Security,

I received a suspicious email that I think might be a phishing attempt. I did NOT click any links.

Details:
- Sender: {sender}
- Subject: "Urgent: Verify your account"
- Contains link to suspicious domain
- Asks for login credentials

I've forwarded it to this address for analysis. Please advise if any action is needed on my part.

{name}"""
        },
        {
            "subject": "Request for additional monitor",
            "body": """Hello,

I'd like to request an additional monitor for my workstation. My current setup with a single screen is limiting my productivity, especially when working with spreadsheets and multiple applications.

My current setup:
- One 24" monitor
- Laptop (docked)

Ideally, I'd like a second matching 24" monitor or larger.

Please let me know the process.

{name}
{department}"""
        },
        {
            "subject": "Email not syncing on mobile",
            "body": """Hi IT,

My work email stopped syncing on my phone yesterday. I've tried removing and re-adding the account but now it won't accept my password (which I know is correct).

Phone: {phone_model}
Email client: {email_client}
Last successful sync: {date}

This is urgent as I need email access while traveling.

{name}"""
        },
        {
            "subject": "Shared drive access request",
            "body": """IT Team,

I need access to the following shared drives for my new project assignment:

1. \\\\server\\{share1}
2. \\\\server\\{share2}
3. \\\\server\\{share3}

Project: {project_name}
Manager approval: {manager}

Please grant read/write access.

Thanks,
{name}"""
        }
    ],

    "partnership": [
        {
            "subject": "Partnership opportunity - complementary products",
            "body": """Dear Business Development Team,

I'm the {title} at {company}, and I believe there's a strong partnership opportunity between our organizations.

Our product {product} complements your offering by {value_prop}. Together, we could provide customers with a more complete solution.

I'd love to explore:
- Integration partnership
- Co-marketing opportunities
- Reseller arrangement

Would you be open to an introductory call?

Best regards,
{name}
{title}
{company}
{website}"""
        },
        {
            "subject": "API integration collaboration",
            "body": """Hello,

We're building {product} and would like to integrate with your platform via API.

Our use case: {use_case}

We have {user_count} active users who would benefit from this integration. This could drive significant traffic and new users to your platform.

Is there a partnerships team I should speak with about this?

{name}
{company}"""
        },
        {
            "subject": "Affiliate program inquiry",
            "body": """Hi,

I run a {type} with {audience_size} followers/subscribers in the {industry} space. Your product is highly relevant to my audience.

I'm interested in joining your affiliate program. Questions:
1. What's the commission structure?
2. Are there promotional materials available?
3. How are referrals tracked?

Looking forward to potentially working together.

{name}
{website}"""
        },
        {
            "subject": "Speaking opportunity at our conference",
            "body": """Dear Team,

I'm organizing {conference_name}, a {industry} conference taking place on {date} in {location}. We expect {attendee_count} attendees.

We'd love to have someone from your company speak about {topic}. This would include:
- 30-minute keynote slot
- Booth in the expo area
- Logo placement on materials

Please let me know if you're interested and who would be the right contact.

Best,
{name}
{title}
{organization}"""
        },
        {
            "subject": "Reseller partnership discussion",
            "body": """Hello Business Development,

{company} is a {description} serving clients in {region}. Our clients frequently ask about solutions like yours.

We're interested in becoming a reseller partner. Our team:
- {sales_team_size} sales representatives
- Established relationships with {client_count}+ companies
- Track record of ${revenue} in software sales annually

What would a reseller partnership look like?

Regards,
{name}
{company}"""
        },
        {
            "subject": "Co-marketing proposal",
            "body": """Hi Marketing Team,

I noticed we share similar target audiences and wondered if you'd be interested in a co-marketing initiative.

Ideas:
1. Joint webinar on {topic}
2. Co-authored industry report
3. Cross-promotional email campaign
4. Shared booth at {conference}

Our marketing reach:
- {email_list_size} email subscribers
- {social_followers} social media followers
- {monthly_visitors} monthly website visitors

Let's discuss!

{name}
{title}, {company}"""
        }
    ],

    "legal": [
        {
            "subject": "Data processing agreement request",
            "body": """Dear Legal Team,

As part of our vendor compliance process, we require a Data Processing Agreement (DPA) before we can proceed with using your service.

Specifically, we need documentation covering:
- GDPR compliance
- Data handling procedures
- Subprocessor list
- Security measures

Please send the DPA or let me know who I should contact.

Regards,
{name}
{title}
{company}"""
        },
        {
            "subject": "GDPR data access request",
            "body": """To Data Protection Officer,

Under GDPR Article 15, I am exercising my right to access personal data you hold about me.

Please provide:
1. Confirmation of whether my data is being processed
2. A copy of all personal data
3. Information about how my data is used
4. Details of any third parties who have access

Email associated with my account: {email}

I expect a response within 30 days as required by law.

{name}"""
        },
        {
            "subject": "Terms of service question - data ownership",
            "body": """Hello,

Before signing up for your enterprise plan, our legal team needs clarification on your Terms of Service, specifically section {section} regarding data ownership.

Questions:
1. Who owns the data we input into your system?
2. What happens to our data if we terminate the agreement?
3. Can our data be used for training AI models?

Please provide written clarification.

{name}
Legal Counsel
{company}"""
        },
        {
            "subject": "NDA required before discussions",
            "body": """Hi,

Before we can share detailed information about our integration requirements, we'll need an NDA in place.

Please review and sign the attached NDA, or send your standard NDA for our review.

We'd like to have this completed within the next week so we can proceed with technical discussions.

Best regards,
{name}
{company}"""
        },
        {
            "subject": "Compliance certification request",
            "body": """Dear Compliance Team,

We're conducting our annual vendor security review. Please provide:

1. SOC 2 Type II report
2. ISO 27001 certification (if applicable)
3. Penetration test summary
4. Business continuity plan overview

This is required for our audit by {date}.

Thank you,
{name}
{title}
{company}"""
        },
        {
            "subject": "Copyright infringement notice",
            "body": """DMCA Takedown Notice

I am writing to notify you that content hosted on your platform infringes my copyright.

Infringing material: {url}
Original work: {original_url}
Copyright registration: {registration_number}

I have a good faith belief that use of the material is not authorized. I declare under penalty of perjury that this notification is accurate.

Please remove the infringing content immediately.

{name}
{title}
{company}
{contact}"""
        }
    ],

    "general": [
        {
            "subject": "Quick question about your product",
            "body": """Hi there,

I have a quick question - does your product support {feature}?

I've looked through your website but couldn't find a clear answer.

Thanks,
{name}"""
        },
        {
            "subject": "How do I get started?",
            "body": """Hello,

I just signed up but I'm not sure where to begin. Is there a getting started guide or tutorial you'd recommend?

Also, are there any tips for new users?

Thanks!
{name}"""
        },
        {
            "subject": "Looking for documentation",
            "body": """Hi,

Where can I find documentation for {feature}? The help center search isn't returning relevant results.

Specifically looking for:
- API documentation
- Integration guides
- Best practices

Thanks,
{name}"""
        },
        {
            "subject": "Company location and hours?",
            "body": """Hello,

I'm trying to find information about your company:
1. Where is your main office located?
2. What are your business hours?
3. Do you have a phone number for general inquiries?

Thanks,
{name}"""
        },
        {
            "subject": "Can I schedule a call?",
            "body": """Hi,

I have several questions that would be easier to discuss over a call rather than email. Is there someone I could schedule a 15-minute call with?

Topics I'd like to cover:
- General product questions
- Implementation approach
- Timeline expectations

Please share available times.

{name}"""
        },
        {
            "subject": "Feedback on new feature",
            "body": """Hi team,

I noticed you recently released {feature}. Just wanted to share some feedback:

What I like:
- {positive1}
- {positive2}

Suggestions:
- {suggestion1}
- {suggestion2}

Overall, keep up the good work!

{name}"""
        },
        {
            "subject": "Newsletter unsubscribe not working",
            "body": """Hello,

I've tried to unsubscribe from your newsletter multiple times but I keep receiving emails. The unsubscribe link doesn't seem to work.

Please remove my email address manually: {email}

Thank you,
{name}"""
        }
    ],

    "spam": [
        {
            "subject": "URGENT: You've Won $1,000,000!!!",
            "body": """CONGRATULATIONS!!!

You have been selected as the WINNER of our international lottery!

To claim your $1,000,000 prize, simply reply with:
- Full name
- Address
- Bank account details
- Social Security Number

ACT NOW - This offer expires in 24 hours!

Best regards,
Dr. James Williams
International Lottery Commission"""
        },
        {
            "subject": "Limited time offer - 90% OFF Designer Goods",
            "body": """MASSIVE CLEARANCE SALE!!!

Get authentic designer goods at 90% OFF retail prices!
- Rolex watches from $50
- Louis Vuitton bags from $30
- Gucci shoes from $25

Click here to shop now: [suspicious-link.com]

Limited stock available! Order today!

Unsubscribe: [link]"""
        },
        {
            "subject": "Your account has been compromised - immediate action required",
            "body": """SECURITY ALERT

We detected unusual activity on your account. Your account will be SUSPENDED unless you verify your identity within 24 hours.

Click here to verify: [fake-login-page.com]

You must provide:
- Username
- Password
- Credit card for verification

Security Team"""
        },
        {
            "subject": "Work from home - Make $5000/week!!!",
            "body": """ARE YOU TIRED OF YOUR 9-5 JOB?

Make $5000-$10000 per week working from home!

NO experience needed!
NO investment required!
Start TODAY!

Thousands of people are already making money with this simple system!

Click to learn the SECRET: [scam-link.com]

To your success,
Mike Johnson"""
        },
        {
            "subject": "Enlarge your... business potential",
            "body": """GROW YOUR BUSINESS FAST!

Our revolutionary supplement will help you:
- Increase energy
- Boost performance
- See results in days!

Doctors don't want you to know this secret!

ORDER NOW and get 50% OFF!

[spam-pharmacy-link.com]"""
        },
        {
            "subject": "Nigerian Prince needs your help",
            "body": """Dear Friend,

I am Prince Abubakar from Nigeria. My late father left $45,000,000 in a bank account which I cannot access due to government restrictions.

I need a foreign partner to help transfer these funds. You will receive 30% ($13,500,000) for your assistance.

Please reply with your:
- Full name
- Phone number
- Bank details

God bless you,
Prince Abubakar"""
        },
        {
            "subject": "Hot singles in your area!",
            "body": """Hey there ;)

There are 47 BEAUTIFUL SINGLES in your area waiting to meet you!

Join FREE today and start chatting NOW!

[dating-spam-site.com]

Click to see who's interested in YOU!

This is not spam. To unsubscribe: [tracking-link.com]"""
        },
        {
            "subject": "RE: Your invoice #INV-29481",
            "body": """Please find attached the invoice you requested.

[malware.exe]

If you have any questions about this invoice, please let me know.

Best regards,
Accounting Department"""
        }
    ]
}


def random_date(start_days_ago=365, end_days_ago=0):
    """Generate a random datetime within the specified range."""
    days_ago = random.randint(end_days_ago, start_days_ago)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    dt = datetime.now() - timedelta(days=days_ago, hours=hours, minutes=minutes)
    return dt.isoformat()


def generate_email_address(name, company=None):
    """Generate a realistic email address."""
    first, last = name.lower().split()[0], name.lower().split()[-1]
    patterns = [
        f"{first}.{last}",
        f"{first}{last}",
        f"{first[0]}{last}",
        f"{first}_{last}",
        f"{first}{random.randint(1, 99)}"
    ]

    if company and random.random() > 0.5:
        domain = company.lower().replace(" ", "").replace(",", "")[:10] + ".com"
    else:
        domain = random.choice(DOMAINS)

    return f"{random.choice(patterns)}@{domain}"


def fill_template(template, name, company):
    """Fill in template placeholders with random data."""
    filled = template

    # Common replacements
    replacements = {
        "{name}": name,
        "{company}": company,
        "{email}": generate_email_address(name, company),
        "{phone}": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "{username}": name.lower().replace(" ", "."),
        "{account_id}": f"ACC-{random.randint(100000, 999999)}",
        "{order_id}": f"ORD-{random.randint(100000, 999999)}",
        "{amount}": str(random.choice([9.99, 19.99, 29.99, 49.99, 99.99, 149.99, 199.99, 299.99, 499.99])),
        "{date}": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%B %d, %Y"),
        "{start_date}": (datetime.now() + timedelta(days=random.randint(7, 60))).strftime("%B %d, %Y"),
        "{end_date}": (datetime.now() + timedelta(days=random.randint(14, 90))).strftime("%B %d, %Y"),
        "{days}": str(random.randint(3, 14)),
        "{hours}": str(random.randint(1, 12)),
        "{years}": str(random.randint(1, 10)),
        "{months}": str(random.randint(1, 12)),
        "{year}": str(random.choice([2023, 2024, 2025])),
        "{size}": str(random.choice([50, 100, 200, 500, 1000, 5000])),
        "{team_size}": str(random.randint(5, 50)),
        "{employee_count}": str(random.randint(5, 50)),
        "{title}": random.choice(["CEO", "CTO", "VP of Engineering", "Director of Operations", "Product Manager", "Senior Developer", "IT Manager"]),
        "{department}": random.choice(["Engineering", "Marketing", "Sales", "Operations", "Finance", "HR", "Product"]),
        "{manager}": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "{balance}": str(random.randint(5, 25)),
        "{budget}": str(random.choice([500, 1000, 2000, 5000, 10000])),
        "{funding_stage}": random.choice(["pre-seed", "seed", "Series A"]),
        "{card_last4}": str(random.randint(1000, 9999)),
        "{tax_id}": f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}",
        "{tickets}": f"#{random.randint(10000, 99999)}, #{random.randint(10000, 99999)}",
        "{original_price}": str(random.choice([29, 49, 79])),
        "{actual_price}": str(random.choice([49, 79, 99, 149])),
        "{rep_name}": f"{random.choice(FIRST_NAMES)} (ID: {random.randint(1000, 9999)})",
        "{time}": f"{random.randint(9, 17)}:{random.randint(0, 59):02d}",
        "{employee_id}": f"EMP{random.randint(10000, 99999)}",
        "{computer_name}": f"WS-{random.randint(100, 999)}",
        "{office_location}": random.choice(["Floor 3, Building A", "Remote", "NYC Office", "SF Office", "London Office"]),
        "{software1}": random.choice(["Adobe Creative Suite", "Visual Studio Code", "Slack", "Zoom"]),
        "{software2}": random.choice(["Python 3.11", "Node.js", "Docker Desktop", "Postman"]),
        "{software3}": random.choice(["Git", "AWS CLI", "Terraform", "Kubernetes"]),
        "{sender}": f"support@{random.choice(['amaz0n', 'paypa1', 'app1e', 'bankofamer1ca'])}.com",
        "{phone_model}": random.choice(["iPhone 15 Pro", "iPhone 14", "Samsung Galaxy S24", "Pixel 8"]),
        "{email_client}": random.choice(["Apple Mail", "Outlook", "Gmail app", "native email app"]),
        "{share1}": random.choice(["Projects", "Marketing", "Engineering"]),
        "{share2}": random.choice(["Reports", "Finance", "Sales"]),
        "{share3}": random.choice(["Archives", "Templates", "Resources"]),
        "{project_name}": random.choice(["Project Phoenix", "Q1 Initiative", "Platform Migration", "Customer Portal"]),
        "{product}": random.choice(["CloudSync", "DataHub", "FlowManager", "InsightPro"]),
        "{value_prop}": random.choice(["automating workflows", "enhancing security", "improving analytics", "streamlining operations"]),
        "{website}": f"www.{company.lower().replace(' ', '')}.com",
        "{use_case}": random.choice(["syncing customer data", "automating reports", "connecting our CRM", "enabling real-time updates"]),
        "{user_count}": str(random.choice([1000, 5000, 10000, 50000, 100000])),
        "{type}": random.choice(["blog", "YouTube channel", "podcast", "newsletter"]),
        "{audience_size}": random.choice(["10,000", "50,000", "100,000", "500,000"]),
        "{industry}": random.choice(["SaaS", "fintech", "healthcare", "e-commerce", "marketing"]),
        "{conference_name}": random.choice(["TechSummit 2025", "SaaS Connect", "Digital Innovation Forum", "Cloud Expo"]),
        "{location}": random.choice(["San Francisco, CA", "New York, NY", "Austin, TX", "Virtual"]),
        "{attendee_count}": str(random.choice([500, 1000, 2500, 5000])),
        "{topic}": random.choice(["AI in enterprise", "scaling startups", "product-led growth", "developer experience"]),
        "{organization}": random.choice(["TechConf Inc", "Industry Events LLC", "Summit Organizers"]),
        "{description}": random.choice(["IT consulting firm", "software distributor", "technology reseller", "managed services provider"]),
        "{region}": random.choice(["North America", "EMEA", "Asia Pacific", "Latin America"]),
        "{sales_team_size}": str(random.randint(10, 100)),
        "{client_count}": str(random.choice([100, 500, 1000, 5000])),
        "{revenue}": random.choice(["1M", "5M", "10M", "50M"]),
        "{email_list_size}": random.choice(["25,000", "50,000", "100,000", "250,000"]),
        "{social_followers}": random.choice(["10,000", "50,000", "100,000", "500,000"]),
        "{monthly_visitors}": random.choice(["50,000", "100,000", "500,000", "1M"]),
        "{conference}": random.choice(["TechCrunch Disrupt", "Web Summit", "SaaStr Annual", "AWS re:Invent"]),
        "{section}": random.choice(["3.2", "4.1", "5.3", "7.2"]),
        "{url}": f"https://example.com/content/{random.randint(1000, 9999)}",
        "{original_url}": f"https://original-content.com/{random.randint(1000, 9999)}",
        "{registration_number}": f"TX{random.randint(1000000, 9999999)}",
        "{contact}": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "{feature}": random.choice(["dark mode", "bulk export", "SSO integration", "custom workflows", "API webhooks"]),
        "{positive1}": random.choice(["Clean interface", "Fast performance", "Easy to use"]),
        "{positive2}": random.choice(["Good documentation", "Helpful onboarding", "Intuitive design"]),
        "{suggestion1}": random.choice(["Add keyboard shortcuts", "Include dark mode", "Better mobile support"]),
        "{suggestion2}": random.choice(["More export options", "Faster sync", "Offline access"]),
        "{systems}": random.choice(["Salesforce, Jira, Confluence", "GitHub, AWS, Slack", "Google Workspace, Asana", "SAP, Oracle, Teams"]),
        "{transaction_id}": f"TXN{random.randint(10000000, 99999999)}",
        "{projects}": str(random.randint(3, 15)),
    }

    for placeholder, value in replacements.items():
        filled = filled.replace(placeholder, value)

    return filled


def generate_email(category):
    """Generate a single email for the given category."""
    templates = EMAIL_TEMPLATES[category]
    template = random.choice(templates)

    sender_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    sender_company = random.choice(COMPANIES)

    # Recipient is typically the company receiving emails
    recipient = random.choice([
        "support@company.com",
        "sales@company.com",
        "billing@company.com",
        "hr@company.com",
        "it@company.com",
        "legal@company.com",
        "info@company.com",
        "partnerships@company.com",
        "hello@company.com"
    ])

    subject = fill_template(template["subject"], sender_name, sender_company)
    body = fill_template(template["body"], sender_name, sender_company)

    # Determine priority based on keywords
    priority = "normal"
    urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
    if any(keyword in subject.lower() or keyword in body.lower() for keyword in urgent_keywords):
        priority = "high"

    return {
        "id": f"email_{random.randint(100000, 999999)}",
        "from": generate_email_address(sender_name, sender_company),
        "from_name": sender_name,
        "to": recipient,
        "subject": subject,
        "body": body,
        "timestamp": random_date(),
        "category": CATEGORIES[category],
        "category_id": category,
        "priority": priority
    }


def generate_corpus(total_emails=300, output_file="email_corpus.json"):
    """Generate a corpus of emails with balanced categories."""
    emails = []

    # Calculate emails per category (roughly balanced)
    categories = list(EMAIL_TEMPLATES.keys())
    base_count = total_emails // len(categories)
    remainder = total_emails % len(categories)

    for i, category in enumerate(categories):
        # Add one extra to some categories to handle remainder
        count = base_count + (1 if i < remainder else 0)
        for _ in range(count):
            emails.append(generate_email(category))

    # Shuffle for randomness
    random.shuffle(emails)

    # Add sequential IDs
    for i, email in enumerate(emails):
        email["id"] = f"email_{i+1:06d}"

    corpus = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_emails": len(emails),
            "categories": CATEGORIES,
            "category_distribution": {cat: sum(1 for e in emails if e["category_id"] == cat) for cat in categories}
        },
        "emails": emails
    }

    with open(output_file, 'w') as f:
        json.dump(corpus, f, indent=2)

    print(f"Generated {len(emails)} emails")
    print(f"Category distribution:")
    for cat, count in corpus["metadata"]["category_distribution"].items():
        print(f"  {CATEGORIES[cat]}: {count}")
    print(f"\nSaved to {output_file}")

    return corpus


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate email corpus for AI categorization training")
    parser.add_argument("-n", "--count", type=int, default=300, help="Number of emails to generate")
    parser.add_argument("-o", "--output", default="email_corpus.json", help="Output file path")
    parser.add_argument("-s", "--seed", type=int, help="Random seed for reproducibility")

    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    generate_corpus(args.count, args.output)
