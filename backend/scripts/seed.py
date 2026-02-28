"""
Seed script — populates Delhi demo data for local service providers.

Usage (from backend/):
    python -m scripts.seed

Idempotent: drops and recreates all data on each run.
Also generates embeddings if OPENAI_API_KEY is set.
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

random.seed(42)

SERVICE_TYPES = [
    # Mechanic services
    {"slug": "car_ac_repair", "name": "Car AC Repair", "category": "mechanic", "description": "Air conditioning repair and gas refilling for cars"},
    {"slug": "engine_oil_change", "name": "Engine Oil Change", "category": "mechanic", "description": "Engine oil and filter replacement service"},
    {"slug": "brake_pad_replacement", "name": "Brake Pad Replacement", "category": "mechanic", "description": "Front and rear brake pad replacement"},
    {"slug": "tire_change", "name": "Tire Change", "category": "mechanic", "description": "Tire replacement and wheel balancing"},
    {"slug": "battery_replacement_car", "name": "Car Battery Replacement", "category": "mechanic", "description": "Car battery testing and replacement"},
    {"slug": "full_car_service", "name": "Full Car Service", "category": "mechanic", "description": "Complete car servicing including oil, filters, and inspection"},
    
    # Electrician services
    {"slug": "house_rewiring", "name": "House Rewiring", "category": "electrician", "description": "Complete electrical wiring for homes"},
    {"slug": "inverter_installation", "name": "Inverter Installation", "category": "electrician", "description": "Home inverter and battery installation"},
    {"slug": "fan_installation", "name": "Ceiling Fan Installation", "category": "electrician", "description": "Ceiling fan fitting and wiring"},
    {"slug": "socket_installation", "name": "Socket Installation", "category": "electrician", "description": "Power socket and switchboard installation"},
    {"slug": "mcb_replacement", "name": "MCB Replacement", "category": "electrician", "description": "Circuit breaker and fuse box replacement"},
    
    # Phone repair services
    {"slug": "phone_screen_repair", "name": "Phone Screen Repair", "category": "phone_repair", "description": "Smartphone screen replacement for all brands"},
    {"slug": "phone_battery_replacement", "name": "Phone Battery Replacement", "category": "phone_repair", "description": "Mobile phone battery replacement"},
    {"slug": "charging_port_repair", "name": "Charging Port Repair", "category": "phone_repair", "description": "Phone charging port repair and replacement"},
]

PRICE_RANGES = {
    "car_ac_repair": (1500, 5000),
    "engine_oil_change": (800, 2500),
    "brake_pad_replacement": (1200, 4000),
    "tire_change": (2000, 8000),
    "battery_replacement_car": (3000, 8000),
    "full_car_service": (2500, 7000),
    "house_rewiring": (5000, 25000),
    "inverter_installation": (8000, 20000),
    "fan_installation": (300, 800),
    "socket_installation": (200, 600),
    "mcb_replacement": (500, 1500),
    "phone_screen_repair": (1000, 5000),
    "phone_battery_replacement": (500, 2000),
    "charging_port_repair": (400, 1200),
}

# Delhi providers with realistic locations
PROVIDERS = [
    {"name": "QuickFix Auto", "category": "mechanic", "address": "14 Connaught Place, New Delhi", "lng": 77.2167, "lat": 28.6315, "phone": "+91 98765 43210", "rating": 4.8, "review_count": 214, "description": "Professional car servicing and AC repair. Same-day service available."},
    {"name": "Delhi Motors", "category": "mechanic", "address": "23 Karol Bagh, Delhi", "lng": 77.1900, "lat": 28.6519, "phone": "+91 98765 43211", "rating": 4.6, "review_count": 156, "description": "Trusted car repair shop. All brands serviced. Free pickup and drop."},
    {"name": "Speed Auto Care", "category": "mechanic", "address": "45 Lajpat Nagar, Delhi", "lng": 77.2436, "lat": 28.5677, "phone": "+91 98765 43212", "rating": 4.3, "review_count": 89, "description": "Quick car repairs and maintenance. Genuine spare parts only."},
    {"name": "City Garage", "category": "mechanic", "address": "12 Nehru Place, Delhi", "lng": 77.2507, "lat": 28.5494, "phone": "+91 98765 43213", "rating": 4.5, "review_count": 132, "description": "Complete car care center. AC repair specialists."},
    {"name": "Auto Expert", "category": "mechanic", "address": "8 Saket, Delhi", "lng": 77.2167, "lat": 28.5244, "phone": "+91 98765 43214", "rating": 4.7, "review_count": 278, "description": "Premium car service center. Trained mechanics and modern equipment."},
    
    {"name": "Bright Electricals", "category": "electrician", "address": "34 Dwarka, Delhi", "lng": 77.0469, "lat": 28.5921, "phone": "+91 98765 43215", "rating": 4.9, "review_count": 327, "description": "Licensed electricians. House wiring and inverter installation experts."},
    {"name": "Power Solutions", "category": "electrician", "address": "56 Rohini, Delhi", "lng": 77.1025, "lat": 28.7489, "phone": "+91 98765 43216", "rating": 4.4, "review_count": 98, "description": "24/7 electrical services. Emergency repairs available."},
    {"name": "Delhi Electricals", "category": "electrician", "address": "78 Janakpuri, Delhi", "lng": 77.0833, "lat": 28.6219, "phone": "+91 98765 43217", "rating": 4.2, "review_count": 67, "description": "Affordable electrical work. Free estimates provided."},
    {"name": "Spark Electric", "category": "electrician", "address": "90 Pitampura, Delhi", "lng": 77.1311, "lat": 28.6942, "phone": "+91 98765 43218", "rating": 4.6, "review_count": 143, "description": "Professional electricians. MCB and wiring specialists."},
    {"name": "Volt Masters", "category": "electrician", "address": "23 Vasant Kunj, Delhi", "lng": 77.1597, "lat": 28.5244, "phone": "+91 98765 43219", "rating": 4.1, "review_count": 54, "description": "Expert electrical contractors. Commercial and residential work."},
    
    {"name": "Mobile Care Center", "category": "phone_repair", "address": "45 Nehru Place, Delhi", "lng": 77.2500, "lat": 28.5489, "phone": "+91 98765 43220", "rating": 4.7, "review_count": 201, "description": "All phone brands repaired. Screen replacement in 30 minutes."},
    {"name": "Phone Fix Delhi", "category": "phone_repair", "address": "67 Lajpat Nagar, Delhi", "lng": 77.2430, "lat": 28.5680, "phone": "+91 98765 43221", "rating": 4.5, "review_count": 189, "description": "Budget-friendly phone repairs. Original and aftermarket parts available."},
    {"name": "Smart Repair Hub", "category": "phone_repair", "address": "89 Connaught Place, Delhi", "lng": 77.2170, "lat": 28.6320, "phone": "+91 98765 43222", "rating": 4.3, "review_count": 76, "description": "iPhone and Android repair specialists. Walk-ins welcome."},
    {"name": "Tech Medics", "category": "phone_repair", "address": "12 Karol Bagh, Delhi", "lng": 77.1905, "lat": 28.6515, "phone": "+91 98765 43223", "rating": 4.0, "review_count": 52, "description": "Phone screen and battery replacement. Same-day service."},
    {"name": "Mobile Clinic", "category": "phone_repair", "address": "34 Saket, Delhi", "lng": 77.2170, "lat": 28.5240, "phone": "+91 98765 43224", "rating": 4.4, "review_count": 115, "description": "Authorized service center for major brands. Warranty on all repairs."},
    
    {"name": "Express Auto Service", "category": "mechanic", "address": "56 Green Park, Delhi", "lng": 77.2069, "lat": 28.5494, "phone": "+91 98765 43225", "rating": 4.6, "review_count": 167, "description": "Fast car servicing. Oil change and brake specialists."},
    {"name": "Reliable Motors", "category": "mechanic", "address": "78 Mayur Vihar, Delhi", "lng": 77.2975, "lat": 28.6089, "phone": "+91 98765 43226", "rating": 4.8, "review_count": 234, "description": "Trusted car repair shop. AC repair and battery replacement."},
    {"name": "Prime Auto Care", "category": "mechanic", "address": "90 Rajouri Garden, Delhi", "lng": 77.1211, "lat": 28.6419, "phone": "+91 98765 43227", "rating": 3.9, "review_count": 48, "description": "Affordable car maintenance. All services under one roof."},
    
    {"name": "Current Electric", "category": "electrician", "address": "12 Shahdara, Delhi", "lng": 77.2864, "lat": 28.6742, "phone": "+91 98765 43228", "rating": 4.7, "review_count": 198, "description": "Residential and commercial electrical work. Licensed contractors."},
    {"name": "Wiring Experts", "category": "electrician", "address": "34 Uttam Nagar, Delhi", "lng": 77.0594, "lat": 28.6219, "phone": "+91 98765 43229", "rating": 4.5, "review_count": 141, "description": "Complete house wiring solutions. Inverter installation specialists."},
]

SOURCE_TYPES = ["scrape", "manual", "receipt", "quote"]


async def seed():
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.mongo_db]

    print("Dropping existing collections...")
    await db.service_types.drop()
    await db.providers.drop()
    await db.observations.drop()

    now = datetime.now(timezone.utc)

    # --- Generate embeddings if possible ---
    embeddings_available = False
    try:
        from app.services.embeddings import build_search_text, get_embeddings, is_available

        if is_available():
            emb = get_embeddings()
            texts = [
                build_search_text(st["name"], st["category"], st.get("description"))
                for st in SERVICE_TYPES
            ]
            vectors = emb.embed_documents(texts)
            for st, vec in zip(SERVICE_TYPES, vectors):
                st["embedding"] = vec
            embeddings_available = True
            print("Generated embeddings for service types.")
    except Exception as e:
        print(f"Skipping embeddings: {e}")

    print(f"Inserting {len(SERVICE_TYPES)} service types...")
    for st in SERVICE_TYPES:
        st["created_at"] = now
    await db.service_types.insert_many(SERVICE_TYPES)

    print(f"Inserting {len(PROVIDERS)} providers...")
    provider_docs = []
    for p in PROVIDERS:
        provider_docs.append({
            "name": p["name"],
            "category": p["category"],
            "address": p["address"],
            "city": "Delhi",
            "phone": p.get("phone"),
            "email": p.get("email"),
            "website": p.get("website"),
            "location": {"type": "Point", "coordinates": [p["lng"], p["lat"]]},
            "rating": p.get("rating"),
            "review_count": p.get("review_count"),
            "description": p.get("description"),
            "created_at": now,
        })
    result = await db.providers.insert_many(provider_docs)
    provider_ids = result.inserted_ids

    print("Generating ~150 observations...")
    observations = []
    for _ in range(150):
        idx = random.randint(0, len(provider_docs) - 1)
        provider = provider_docs[idx]
        provider_id = provider_ids[idx]

        service = random.choice(SERVICE_TYPES)
        low, high = PRICE_RANGES[service["slug"]]
        price = round(random.uniform(low, high), 2)

        days_ago = random.randint(0, 90)
        observed_at = now - timedelta(days=days_ago)

        observations.append({
            "provider_id": provider_id,
            "service_type": service["slug"],
            "category": service["category"],
            "price": price,
            "currency": "INR",
            "source_type": random.choice(SOURCE_TYPES),
            "location": provider["location"],
            "observed_at": observed_at,
            "created_at": now,
        })

    await db.observations.insert_many(observations)

    from pymongo import GEOSPHERE
    await db.service_types.create_index("slug", unique=True)
    await db.providers.create_index([("location", GEOSPHERE)])
    await db.observations.create_index([("location", GEOSPHERE)])
    await db.observations.create_index([("category", 1), ("service_type", 1)])

    embed_note = " (with embeddings)" if embeddings_available else " (no embeddings — run embed_service_types)"
    print(f"Done! Seeded {len(SERVICE_TYPES)} service types, {len(PROVIDERS)} providers, {len(observations)} observations{embed_note}.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
