"""Database of exercises for workout templates."""

EXERCISE_DB = {
    "Push (Chest/Shoulders/Triceps)": [
        "Bench Press (Barbell)",
        "Bench Press (Dumbbell)",
        "Incline Bench Press",
        "Overhead Press (Barbell)",
        "Overhead Press (Dumbbell)",
        "Lateral Raises",
        "Cable Lateral Raises",
        "Tricep Pushdowns (Cable)",
        "Overhead Tricep Ext (Cable)",
        "Skullcrushers",
        "Dips",
        "Push-ups",
        "Cable Crossovers/Flyes"
    ],
    "Pull (Back/Biceps)": [
        "Deadlift",
        "Pull-ups",
        "Lat Pulldowns (Cable)",
        "Seated Cable Rows",
        "Barbell Rows",
        "Dumbbell Rows",
        "Face Pulls (Cable)",
        "Barbell Curls",
        "Hammer Curls",
        "Preacher Curls",
        "Cable Bicep Curls",
        "Chin-ups"
    ],
    "Legs (Quads/Hams/Calves)": [
        "Squat (Barbell)",
        "Leg Press",
        "Romanian Deadlift",
        "Leg Extensions",
        "Leg Curls",
        "Lunges",
        "Bulgarian Split Squats",
        "Calf Raises (Standing)",
        "Calf Raises (Seated)"
    ],
    "Core": [
        "Plank",
        "Crunches",
        "Leg Raises",
        "Ab Wheel Rollout",
        "Russian Twists"
    ],
    "Cardio": [
        "Treadmill Run",
        "Cycling",
        "Elliptical",
        "Rowing Machine",
        "Jump Rope"
    ]
}

FAMOUS_SPLITS = {
    "Bro Split": ["Chest", "Back", "Legs", "Shoulders", "Arms"],
    "Push Pull Legs (PPL)": ["Push", "Pull", "Legs"],
    "Upper Lower": ["Upper Body", "Lower Body"],
    "Full Body": ["Full Body"]
}

# Flatten for type lookup
EXERCISE_TYPES = {}
for category, exercises in EXERCISE_DB.items():
    type_ = "Cardio" if category == "Cardio" else "Strength"
    for ex in exercises:
        EXERCISE_TYPES[ex] = type_
