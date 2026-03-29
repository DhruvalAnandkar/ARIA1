// Initialize ARIA MongoDB database
db = db.getSiblingDB("aria");

// Create collections with indexes
db.createCollection("user_profiles");
db.user_profiles.createIndex({ user_id: 1 }, { unique: true });

db.createCollection("user_preferences");
db.user_preferences.createIndex({ user_id: 1 }, { unique: true });
