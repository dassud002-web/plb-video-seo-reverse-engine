#!/usr/bin/env python3
"""
Character Universe Engine for PLB Story Universe Factory
=========================================================
Builds a dual-layer character universe:
1. CANON CHARACTERS: Directly grounded in video forensic evidence.
2. CREATIVE CHARACTER POOL: Compatible, rich animal catalog with physical,
   temperament, movement, and comedic attributes.
Provides 15 Character Mutation Operators to drive deep narrative evolution.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum
import random

class CharacterMutationOperator(str, Enum):
    KEEP = "KEEP"
    SWAP = "SWAP"
    ADD = "ADD"
    REMOVE = "REMOVE"
    REPLACE = "REPLACE"
    SPECIES_CROSSOVER = "SPECIES_CROSSOVER"
    ROLE_REVERSAL = "ROLE_REVERSAL"
    PARENT_CUB = "PARENT_CUB"
    SIBLING_PAIR = "SIBLING_PAIR"
    FRIEND_PAIR = "FRIEND_PAIR"
    RIVAL_PAIR = "RIVAL_PAIR"
    MENTOR_STUDENT = "MENTOR_STUDENT"
    PROTECTOR_COMPANION = "PROTECTOR_COMPANION"
    STRANGER_PAIR = "STRANGER_PAIR"
    GROUP_CAST = "GROUP_CAST"

@dataclass
class CharacterProfile:
    id: str
    name: str
    species: str
    breed: str = ""
    age_class: str = "Adult"      # Baby, Juvenile, Adult, Senior
    size_class: str = "Medium"    # Micro, Small, Medium, Large
    temperament: str = "Curious"   # Curious, Bold, Timid, Mischievous, Stoic, Energetic, Clumsy, Dignified
    natural_behavior: str = "Investigative foraging"
    movement_style: str = "Agile trot"
    comedy_style: str = "Physical slapstick"
    compatibility: List[str] = field(default_factory=list)
    role_options: List[str] = field(default_factory=lambda: ["Protagonist", "Sidekick"])
    is_canon: bool = False
    source_evidence_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterProfile":
        return cls(**data)

# Controlled Library of Safe, Domestic, Friendly Animals
CREATIVE_ANIMAL_TEMPLATES: List[Dict[str, Any]] = [
    {
        "species": "Dog",
        "breed": "Golden Retriever Pup",
        "age_class": "Baby",
        "size_class": "Small",
        "temperament": "Over-Excited & Clumsy",
        "natural_behavior": "Tail-wagging tumble, nose boops",
        "movement_style": "Wobbly galloping with sudden skids",
        "comedy_style": "Exaggerated innocent enthusiasm",
        "compatibility": ["Duck", "Chicken", "Rabbit", "Cat", "Goat", "Piglet"],
        "role_options": ["Eager Rookie", "Accidental Chaos Agent", "Brave Protege"]
    },
    {
        "species": "Duck",
        "breed": "Pekin Duck",
        "age_class": "Adult",
        "size_class": "Medium",
        "temperament": "Confident & Pretentious",
        "natural_behavior": "Synchronized waddling, water splashing",
        "movement_style": "Rhythmic bobbing walk, sudden flapping sprint",
        "comedy_style": "Indignant quacking, ruffled feathers",
        "compatibility": ["Dog", "Rabbit", "Chicken", "Turtle", "Piglet"],
        "role_options": ["Proud Leader", "Skeptical Inspector", "Reluctant Companion"]
    },
    {
        "species": "Duckling",
        "breed": "Yellow Runner Duckling",
        "age_class": "Baby",
        "size_class": "Micro",
        "temperament": "Fearless & Inquisitive",
        "natural_behavior": "Single-file marching, rapid head tilting",
        "movement_style": "Tiny hyperactive patter",
        "comedy_style": "Tiniest creature giving orders to giants",
        "compatibility": ["Duck", "Dog", "Cat", "Chicken", "Lamb"],
        "role_options": ["Innocent Leader", "Audacious Explorer", "Mischievous Shadow"]
    },
    {
        "species": "Rabbit",
        "breed": "Holland Lop",
        "age_class": "Juvenile",
        "size_class": "Small",
        "temperament": "Cautious & Hyper-Alert",
        "natural_behavior": "Nose twitching, thumping hind feet",
        "movement_style": "Zippy darting hops, freeze-frames",
        "comedy_style": "Direct-to-camera shocked stares, dramatic binkies",
        "compatibility": ["Guinea Pig", "Tortoise", "Duck", "Chicken", "Cat"],
        "role_options": ["Anxious Strategist", "Snack Connoisseur", "Undercover Scout"]
    },
    {
        "species": "Chicken",
        "breed": "Fluffy Silkie Hen",
        "age_class": "Adult",
        "size_class": "Small",
        "temperament": "Dignified & Aristocratic",
        "natural_behavior": "Pompous perching, methodical ground inspection",
        "movement_style": "Regal glide followed by chaotic panic flutters",
        "comedy_style": "Haughty composure broken by a single sour peck",
        "compatibility": ["Dog", "Duck", "Goat", "Piglet", "Rabbit"],
        "role_options": ["Royalty in Disguise", "Stern Headmistress", "Drama Queen"]
    },
    {
        "species": "Chick",
        "breed": "Fluffy Bantam Chick",
        "age_class": "Baby",
        "size_class": "Micro",
        "temperament": "Cheeky & Boundless",
        "natural_behavior": "Peeping chorus, mimicking adults",
        "movement_style": "Bouncing ball hops",
        "comedy_style": "Attempting huge leaps across microscopic gaps",
        "compatibility": ["Chicken", "Duckling", "Rabbit", "Dog"],
        "role_options": ["Apprentice", "Cheerleader", "Secret Mastermind"]
    },
    {
        "species": "Goat",
        "breed": "Nigerian Dwarf Kid",
        "age_class": "Baby",
        "size_class": "Small",
        "temperament": "Mischievous Acrobat",
        "natural_behavior": "Head butting wooden fences, parkour jumping",
        "movement_style": "Spastic sideways spring jumps",
        "comedy_style": "Climbing on top of sleepy companions",
        "compatibility": ["Sheep", "Alpaca", "Dog", "Pony", "Piglet"],
        "role_options": ["Daredevil", "Fence Jumper", "Comedic Instigator"]
    },
    {
        "species": "Lamb",
        "breed": "Baby Babydoll Sheep",
        "age_class": "Baby",
        "size_class": "Small",
        "temperament": "Gentle & Affectionate",
        "natural_behavior": "Nuzzling wool, bleating softly",
        "movement_style": "Spring-loaded pounces on green grass",
        "comedy_style": "Getting stuck in tiny flowerpots",
        "compatibility": ["Goat", "Dog", "Duck", "Alpaca"],
        "role_options": ["Sweet Peacemaker", "Soft Companion", "Sleepy Hero"]
    },
    {
        "species": "Piglet",
        "breed": "Spotted Teacup Piglet",
        "age_class": "Baby",
        "size_class": "Micro",
        "temperament": "Determined Glutton",
        "natural_behavior": "Mud snuffling, high-pitched squeals",
        "movement_style": "Tiny trotters racing toward anything edible",
        "comedy_style": "Slides across wet surfaces like a curling stone",
        "compatibility": ["Dog", "Duck", "Chicken", "Goat"],
        "role_options": ["Heist Specialist", "Hungry Sidekick", "Bulldozer"]
    },
    {
        "species": "Cat",
        "breed": "Domestic Tabby",
        "age_class": "Adult",
        "size_class": "Small",
        "temperament": "Aloof Cynic",
        "natural_behavior": "Slow blinking, pushing objects off tables",
        "movement_style": "Silent liquid stalking",
        "comedy_style": "Unfazed judge watching others fail",
        "compatibility": ["Dog", "Rabbit", "Parrot", "Horse"],
        "role_options": ["Sarcastic Observer", "Reluctant Master", "Secret Ally"]
    },
    {
        "species": "Turtle",
        "breed": "Red-Eared Slider",
        "age_class": "Senior",
        "size_class": "Small",
        "temperament": "Patient Philosopher",
        "natural_behavior": "Basking on warm flat stones, unhurried neck stretch",
        "movement_style": "Slow, deliberate, unstoppable crawling",
        "comedy_style": "Winning races simply because everyone else got distracted",
        "compatibility": ["Duck", "Rabbit", "Fish", "Chicken"],
        "role_options": ["Ancient Guru", "Unflappable Anchor", "The Witness"]
    },
    {
        "species": "Pony",
        "breed": "Miniature Shetland Pony",
        "age_class": "Adult",
        "size_class": "Medium",
        "temperament": "Stubborn & Loyal",
        "natural_behavior": "Mane shaking, demanding carrots",
        "movement_style": "Sturdy clip-clop stride",
        "comedy_style": "Blocking doorways by standing completely still",
        "compatibility": ["Dog", "Goat", "Lamb", "Chicken"],
        "role_options": ["Gentle Giant", "The Bouncer", "Unmovable Guardian"]
    },
    {
        "species": "Alpaca",
        "breed": "Huacaya Alpaca",
        "age_class": "Juvenile",
        "size_class": "Large",
        "temperament": "Curious & Dramatic",
        "natural_behavior": "Humming vocalizations, neck crane inspection",
        "movement_style": "Bouncy graceful prance",
        "comedy_style": "Overly dramatic side-eye reactions",
        "compatibility": ["Goat", "Sheep", "Dog"],
        "role_options": ["Drama Royalty", "Towering Observer", "Warm Guardian"]
    },
    {
        "species": "Parrot",
        "breed": "Green Conure",
        "age_class": "Adult",
        "size_class": "Micro",
        "temperament": "Noisy Commentator",
        "natural_behavior": "Head bobbing, mimicking background noises",
        "movement_style": "Fluttering dive-bombs",
        "comedy_style": "Narrating everybody's mistakes in real-time",
        "compatibility": ["Cat", "Dog", "Rabbit"],
        "role_options": ["The Town Crier", "Annoying Sibling", "Spy in the Sky"]
    },
    {
        "species": "Hamster",
        "breed": "Roborovski Dwarf",
        "age_class": "Juvenile",
        "size_class": "Micro",
        "temperament": "Speed Demon",
        "natural_behavior": "Cheek pouch stuffing, wheel spinning",
        "movement_style": "Blur speed scurrying",
        "comedy_style": "Cheeks 3x the size of its head",
        "compatibility": ["Guinea Pig", "Rabbit", "Turtle"],
        "role_options": ["Hyperactive Scout", "Pouch Smuggler", "Micro Hero"]
    },
    {
        "species": "Guinea Pig",
        "breed": "Abyssinian Swirl",
        "age_class": "Adult",
        "size_class": "Micro",
        "temperament": "Vocal Alarm Bell",
        "natural_behavior": "Wheeking at the sound of rustling plastic",
        "movement_style": "Low-slung furry potato scoot",
        "comedy_style": "Freezing in popcorn jumps when excited",
        "compatibility": ["Rabbit", "Hamster", "Turtle", "Duckling"],
        "role_options": ["Alarm System", "Cuddle Enthusiast", "Potato Mascot"]
    },
    {
        "species": "Dog",
        "breed": "Welsh Corgi Pup",
        "age_class": "Baby",
        "size_class": "Small",
        "temperament": "High-Spirited Lowrider",
        "natural_behavior": "Short-leg sprint waddle, floor sploots",
        "movement_style": "Aerodynamic potato trot",
        "comedy_style": "Cannot reach tall surfaces, dramatic huffs",
        "compatibility": ["Duck", "Chicken", "Cat", "Goat"],
        "role_options": ["Lowrider Hero", "Stubborn Patrol", "Fluffy Mascot"]
    },
    {
        "species": "Dog",
        "breed": "Border Collie Junior",
        "age_class": "Juvenile",
        "size_class": "Medium",
        "temperament": "Hyper-Focused Overthinker",
        "natural_behavior": "Herding imaginary ducks, intense eye contact",
        "movement_style": "Low stealth crouch and explosive sprint",
        "comedy_style": "Tries to herd butterflies and garden hoses",
        "compatibility": ["Sheep", "Duck", "Goat", "Cat"],
        "role_options": ["The Mastermind", "Overthinking Scout", "Flock Manager"]
    },
    {
        "species": "Cat",
        "breed": "Siamese Detective",
        "age_class": "Adult",
        "size_class": "Small",
        "temperament": "Vocal & Inquisitive",
        "natural_behavior": "Investigating closed boxes, loud chatter",
        "movement_style": "Graceful balletic stalks",
        "comedy_style": "Dramatically offended by any loud noise",
        "compatibility": ["Dog", "Parrot", "Rabbit"],
        "role_options": ["Private Investigator", "Chirpy Critic", "Shadow Master"]
    },
    {
        "species": "Cat",
        "breed": "Maine Coon Kitten",
        "age_class": "Baby",
        "size_class": "Medium",
        "temperament": "Gentle Fluff Titan",
        "natural_behavior": "Giant paws batting gentle taps",
        "movement_style": "Big bouncy pounces",
        "comedy_style": "Doesn't realize how big it is already",
        "compatibility": ["Dog", "Rabbit", "Duckling"],
        "role_options": ["Gentle Giant", "Warm Blanket", "Protector Pup"]
    },
    {
        "species": "Rabbit",
        "breed": "Flemish Giant",
        "age_class": "Adult",
        "size_class": "Medium",
        "temperament": "Stoic Heavyweight",
        "natural_behavior": "Sprawling across entire floor mats, slow nose twitches",
        "movement_style": "Deep thumping slow hops",
        "comedy_style": "Smaller animals mistake it for a furry sofa",
        "compatibility": ["Guinea Pig", "Hamster", "Dog", "Duck"],
        "role_options": ["The Anchor", "Wise Elder", "Furry Fortress"]
    },
    {
        "species": "Duck",
        "breed": "White Call Duck",
        "age_class": "Adult",
        "size_class": "Micro",
        "temperament": "Screaming Pocket Quacker",
        "natural_behavior": "Rapid high-frequency quacking, puddle dives",
        "movement_style": "Miniature frantic paddle waddle",
        "comedy_style": "Loudest voice on the farm despite being tiny",
        "compatibility": ["Duckling", "Chicken", "Pony"],
        "role_options": ["Alarm Clock", "Megaphone", "Pocket Dynamo"]
    },
    {
        "species": "Goat",
        "breed": "Pygmy Parkour Kid",
        "age_class": "Baby",
        "size_class": "Micro",
        "temperament": "Zero-Fear Hopper",
        "natural_behavior": "Jumping onto hay bales, nibbling shirt buttons",
        "movement_style": "Springboard diagonal hops",
        "comedy_style": "Lands on sleeping dogs with zero apology",
        "compatibility": ["Dog", "Lamb", "Piglet"],
        "role_options": ["Acrobat", "Chaos Catalyst", "Spring Master"]
    },
    {
        "species": "Piglet",
        "breed": "Berkshire Snuffler",
        "age_class": "Baby",
        "size_class": "Small",
        "temperament": "Mud Scientist",
        "natural_behavior": "Detailed soil analysis with snout",
        "movement_style": "Rhythmic chunky trot",
        "comedy_style": "Immediate nap inside fresh laundry baskets",
        "compatibility": ["Dog", "Goat", "Duck"],
        "role_options": ["Snack Tracker", "Mud Connoisseur", "Heavy Dozer"]
    },
    {
        "species": "Turtle",
        "breed": "Eastern Box Turtle",
        "age_class": "Senior",
        "size_class": "Micro",
        "temperament": "Quiet Contemplative",
        "natural_behavior": "Hiding in shell then peeking one golden eye",
        "movement_style": "Stealth botanical glide",
        "comedy_style": "Disappears into clover patch in plain sight",
        "compatibility": ["Rabbit", "Duck", "Fish"],
        "role_options": ["Stealth Infiltrator", "Clover Ninja", "The Witness"]
    },
    {
        "species": "Hedgehog",
        "breed": "African Pygmy Hedgehog",
        "age_class": "Juvenile",
        "size_class": "Micro",
        "temperament": "Spiky Introvert",
        "natural_behavior": "Curling into protective quill sphere, nose snuffling",
        "movement_style": "Miniature tank roll and scurry",
        "comedy_style": "Pop-quill startle reaction when leaves crunch",
        "compatibility": ["Hamster", "Turtle", "Guinea Pig"],
        "role_options": ["Spike Scout", "Night Watcher", "Pocket Shield"]
    }
]

def extract_canon_characters(evidence: Dict[str, Any], story_dna: Dict[str, Any]) -> List[CharacterProfile]:
    """
    Extracts the canonical character profiles directly observed in the source video.
    Grounded in video timeline evidence and visual intelligence.
    """
    domains = evidence.get("domains", {})
    char_fact = domains.get("characters", {}).get("fact", "Observed foreground animal")
    char_infer = domains.get("characters", {}).get("inference", "Protagonist")
    char_count = domains.get("characters", {}).get("count", 1)
    ev_refs = evidence.get("evidence_items", [])
    ref_id = ev_refs[0].get("evidence_id") if ev_refs else "EV-CONTAINER"

    canon_list: List[CharacterProfile] = []

    # Parse primary canon subject
    primary_name = char_infer.split(" / ")[0].strip() if " / " in char_infer else char_infer.strip()
    if primary_name.lower().startswith("identified as "):
        primary_name = primary_name[14:].strip().title()

    profile_name = evidence.get("visual_profile_name") or story_dna.get("visual_profile")
    is_explicit_generic = (profile_name == "generic")

    # Build comprehensive search context across evidence, domains, story DNA, and observed claims
    search_context_parts = [
        char_infer,
        char_fact,
        evidence.get("source_video_name", ""),
        story_dna.get("core_premise", "")
    ]
    for c in story_dna.get("characters", []):
        search_context_parts.append(c.get("name", ""))
        search_context_parts.append(c.get("observed_fact", ""))
    for item in ev_refs:
        search_context_parts.append(item.get("claim", ""))
    
    lower_inf = " ".join(search_context_parts).lower()
    if not is_explicit_generic and (profile_name == "duck_sprinkler" or (not profile_name and "duck" in lower_inf and "puppy" in lower_inf)):
        canon_list.append(CharacterProfile(
            id="CHAR-CANON-01",
            name="Pekin Duck",
            species="Duck",
            breed="Pekin Duck",
            age_class="Adult",
            size_class="Medium",
            temperament="Confident & Swift",
            natural_behavior="Waddling sprint through water spray",
            movement_style="Agile low-flying flap and run",
            comedy_style="Indignant wet quacks",
            compatibility=["Dog", "Duckling", "Chicken"],
            role_options=["Leader", "The Sprinter", "Water Guide"],
            is_canon=True,
            source_evidence_ref=ref_id
        ))
        canon_list.append(CharacterProfile(
            id="CHAR-CANON-02",
            name="Black Puppy",
            species="Dog",
            breed="Labrador Mix Pup",
            age_class="Baby",
            size_class="Small",
            temperament="Boundless Joy & Playful",
            natural_behavior="Tail-wagging pursuit, splash bites",
            movement_style="Enthusiastic gallop with wet skids",
            comedy_style="Synchronized double shake",
            compatibility=["Duck", "Cat", "Goat"],
            role_options=["The Chaser", "Joyful Companion", "Best Friend"],
            is_canon=True,
            source_evidence_ref=ref_id
        ))
        return canon_list

    elif not is_explicit_generic and (profile_name == "chicken_coop_lime" or (not profile_name and ("silkie" in lower_inf or ("chicken" in lower_inf and "coop" in lower_inf)))):
        canon_list.append(CharacterProfile(
            id="CHAR-CANON-01",
            name="White Silkie",
            species="Chicken",
            breed="Silkie Hen",
            age_class="Adult",
            size_class="Small",
            temperament="Dignified & Curious",
            natural_behavior="Perch inspection, cautious pecking",
            movement_style="Gentle puffed glide",
            comedy_style="Comedic sour head tilt recoil",
            compatibility=["Dog", "Chick", "Duck", "Goat"],
            role_options=["The Taster", "Dignified Critic", "Flock Elder"],
            is_canon=True,
            source_evidence_ref=ref_id
        ))
        if "barred" in lower_inf or char_count >= 2:
            canon_list.append(CharacterProfile(
                id="CHAR-CANON-02",
                name="Barred Rock Hen",
                species="Chicken",
                breed="Plymouth Barred Rock",
                age_class="Adult",
                size_class="Medium",
                temperament="Skeptical Onlooker",
                natural_behavior="Perch sentry, side-eye observation",
                movement_style="Sturdy strut",
                comedy_style="Smug indifference while friend recoils",
                compatibility=["Silkie", "Chicks", "Duck"],
                role_options=["The Skeptic", "Loyal Buddy", "Flock Guard"],
                is_canon=True,
                source_evidence_ref=ref_id
            ))
        return canon_list

    elif not is_explicit_generic and (profile_name == "rabbits_horseradish" or (not profile_name and ("rabbit" in lower_inf and "horseradish" in lower_inf))):
        canon_list.append(CharacterProfile(
            id="CHAR-CANON-01",
            name="Spotted Bunny",
            species="Rabbit",
            breed="Spotted Dutch Rabbit",
            age_class="Juvenile",
            size_class="Small",
            temperament="Curious & Direct",
            natural_behavior="Table sniffing, decisive crunch bites",
            movement_style="Fast twitch hops",
            comedy_style="Motionless wide-eyed stare into camera lens",
            compatibility=["Guinea Pig", "Tortoise", "Dog"],
            role_options=["Brave Nibbler", "Camera Fixer", "Snack King"],
            is_canon=True,
            source_evidence_ref=ref_id
        ))
        canon_list.append(CharacterProfile(
            id="CHAR-CANON-02",
            name="White Bunny",
            species="Rabbit",
            breed="Florida White",
            age_class="Juvenile",
            size_class="Small",
            temperament="Timid Mimic",
            natural_behavior="Huddling behind companions",
            movement_style="Nervous darting",
            comedy_style="Backing away after one sniff",
            compatibility=["Spotted Bunny", "Hamster"],
            role_options=["The Cautious One", "Echo Nibbler", "Gentle Companion"],
            is_canon=True,
            source_evidence_ref=ref_id
        ))
        return canon_list

    elif not is_explicit_generic and (profile_name == "turtles_grapefruit" or (not profile_name and ("turtle" in lower_inf and "grapefruit" in lower_inf))):
        canon_list.append(CharacterProfile(
            id="CHAR-CANON-01",
            name="Slider Turtle",
            species="Turtle",
            breed="Red-Eared Slider",
            age_class="Senior",
            size_class="Small",
            temperament="Determined & Unhurried",
            natural_behavior="Slow stone crawl, wide-mouth bite",
            movement_style="Unstoppable crawl",
            comedy_style="Biting fruit twice its own head size",
            compatibility=["Duck", "Fish", "Tortoise"],
            role_options=["Ancient Feaster", "The Tank", "Relic Explorer"],
            is_canon=True,
            source_evidence_ref=ref_id
        ))
        return canon_list

    # Fallback generic canon character: strictly grounded in video evidence
    if not primary_name or primary_name.lower() in ["protagonist", "entity", "subject", "lead subject"]:
        src_name = evidence.get("source_video_name", "")
        from scripts.video_seo_reverse_engineer import sanitize_filename_tokens
        clean_toks = sanitize_filename_tokens(src_name)
        if clean_toks and clean_toks.lower() not in ["video", "vid", "clip", "ref", "test", "target"]:
            primary_name = clean_toks.title()
        else:
            primary_name = "Lead Protagonist"

    inferred_species = "Domestic Companion"
    lower_name = primary_name.lower()
    for sp in ["fox", "dog", "cat", "bear", "rabbit", "horse", "wolf", "tiger", "lion", "duck", "chicken", "hen", "bird", "drone", "robot", "human"]:
        if sp in lower_name:
            inferred_species = sp.capitalize()
            break

    canon_list.append(CharacterProfile(
        id="CHAR-CANON-01",
        name=primary_name,
        species=inferred_species,
        breed="Authentic Specimen",
        age_class="Adult",
        size_class="Medium",
        temperament="Investigative & Alert",
        natural_behavior=char_fact,
        movement_style="Authentic kinetic motion",
        comedy_style="Candid natural reaction",
        compatibility=["Dog", "Cat", "Duck", "Rabbit"],
        role_options=["Protagonist", "Lead Subject"],
        is_canon=True,
        source_evidence_ref=ref_id
    ))
    return canon_list

def build_character_universe(
    canon_characters: List[CharacterProfile],
    pool_size: int = 20
) -> Dict[str, Any]:
    """
    Builds the complete Character Universe combining Canon and Creative Pools.
    """
    creative_pool: List[CharacterProfile] = []
    canon_species = {c.species.lower() for c in canon_characters}

    # Generate creative characters from templates with unique personality names
    for idx, tmpl in enumerate(CREATIVE_ANIMAL_TEMPLATES[:pool_size], 1):
        char_id = f"CHAR-CREATIVE-{idx:02d}"
        char_name = f"{tmpl['breed']} '{tmpl['species']}'"
        creative_pool.append(CharacterProfile(
            id=char_id,
            name=char_name,
            species=tmpl["species"],
            breed=tmpl["breed"],
            age_class=tmpl["age_class"],
            size_class=tmpl["size_class"],
            temperament=tmpl["temperament"],
            natural_behavior=tmpl["natural_behavior"],
            movement_style=tmpl["movement_style"],
            comedy_style=tmpl["comedy_style"],
            compatibility=tmpl["compatibility"],
            role_options=tmpl["role_options"],
            is_canon=False,
            source_evidence_ref="Creative Expansion Pool"
        ))

    return {
        "canon_characters": [c.to_dict() for c in canon_characters],
        "creative_pool": [c.to_dict() for c in creative_pool],
        "total_characters": len(canon_characters) + len(creative_pool),
        "canon_count": len(canon_characters),
        "creative_count": len(creative_pool),
        "unique_species": list(set([c.species for c in canon_characters] + [c.species for c in creative_pool]))
    }

def apply_character_mutation(
    parent_characters: List[Dict[str, Any]],
    operator: CharacterMutationOperator,
    character_pool: List[Dict[str, Any]],
    canon_characters: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Applies one of the 15 Character Mutation Operators to generate an evolved ensemble.
    Returns: (new_characters, mutation_metadata)
    """
    all_available = canon_characters + character_pool
    p_chars = [c for c in parent_characters]
    p_names = {c.get("name") for c in p_chars}

    new_chars: List[Dict[str, Any]] = []
    inherited_names: List[str] = []
    introduced_names: List[str] = []
    removed_names: List[str] = []

    if operator == CharacterMutationOperator.KEEP or not p_chars:
        new_chars = [copy_char(c) for c in p_chars]
        inherited_names = list(p_names)

    elif operator == CharacterMutationOperator.SWAP:
        if len(p_chars) >= 2:
            new_chars = [copy_char(p_chars[1]), copy_char(p_chars[0])] + [copy_char(c) for c in p_chars[2:]]
            new_chars[0]["role"] = "New Protagonist (Swapped)"
            new_chars[1]["role"] = "New Companion (Swapped)"
            inherited_names = list(p_names)
        else:
            new_chars = [copy_char(c) for c in p_chars]
            inherited_names = list(p_names)

    elif operator == CharacterMutationOperator.ADD:
        new_chars = [copy_char(c) for c in p_chars]
        inherited_names = list(p_names)
        # Pick an unpicked compatible creative character
        candidates = [c for c in all_available if c.get("name") not in p_names]
        chosen = random.choice(candidates) if candidates else random.choice(all_available)
        c_add = copy_char(chosen)
        c_add["role"] = "Newly Arrived Ally"
        new_chars.append(c_add)
        introduced_names.append(c_add.get("name"))

    elif operator == CharacterMutationOperator.REMOVE:
        if len(p_chars) > 1:
            new_chars = [copy_char(p_chars[0])]
            inherited_names = [p_chars[0].get("name")]
            removed_names = [c.get("name") for c in p_chars[1:]]
        else:
            new_chars = [copy_char(c) for c in p_chars]
            inherited_names = list(p_names)

    elif operator == CharacterMutationOperator.REPLACE:
        if p_chars:
            survivor = copy_char(p_chars[0])
            new_chars.append(survivor)
            inherited_names.append(survivor.get("name"))
            if len(p_chars) > 1:
                removed_names.append(p_chars[1].get("name"))
            candidates = [c for c in all_available if c.get("name") not in p_names]
            chosen = random.choice(candidates) if candidates else random.choice(all_available)
            c_rep = copy_char(chosen)
            c_rep["role"] = "Substitute Partner"
            new_chars.append(c_rep)
            introduced_names.append(c_rep.get("name"))
        else:
            new_chars = [copy_char(c) for c in canon_characters]
            inherited_names = [c.get("name") for c in new_chars]

    elif operator == CharacterMutationOperator.SPECIES_CROSSOVER:
        # Cross primary canon with an unexpected creative animal species (e.g. Chicken + Piglet or Dog + Turtle)
        primary = copy_char(p_chars[0]) if p_chars else copy_char(canon_characters[0])
        inherited_names.append(primary.get("name"))
        crossover_cands = [c for c in all_available if c.get("species") != primary.get("species")]
        crossover_partner = copy_char(random.choice(crossover_cands) if crossover_cands else all_available[0])
        crossover_partner["role"] = f"Crossover Partner ({crossover_partner.get('species')})"
        new_chars = [primary, crossover_partner]
        introduced_names.append(crossover_partner.get("name"))

    elif operator == CharacterMutationOperator.PARENT_CUB:
        # Form an adult + baby pair of the same or neighboring species
        primary = copy_char(p_chars[0]) if p_chars else copy_char(canon_characters[0])
        primary["age_class"] = "Adult"
        primary["role"] = "Parent Guardian"
        new_chars.append(primary)
        inherited_names.append(primary.get("name"))
        cub_cands = [c for c in all_available if c.get("age_class") == "Baby"]
        cub = copy_char(random.choice(cub_cands) if cub_cands else all_available[0])
        cub["role"] = "Curious Baby / Cub"
        new_chars.append(cub)
        introduced_names.append(cub.get("name"))

    elif operator == CharacterMutationOperator.SIBLING_PAIR:
        # Pair with an identical or same-species juvenile sibling
        primary = copy_char(p_chars[0]) if p_chars else copy_char(canon_characters[0])
        new_chars.append(primary)
        inherited_names.append(primary.get("name"))
        sibling = copy_char(primary)
        sibling["name"] = f"Sibling {primary.get('name')}"
        sibling["temperament"] = "Playful Rival"
        sibling["role"] = "Mischievous Sibling"
        new_chars.append(sibling)
        introduced_names.append(sibling.get("name"))

    elif operator == CharacterMutationOperator.MENTOR_STUDENT:
        primary = copy_char(p_chars[0]) if p_chars else copy_char(canon_characters[0])
        primary["role"] = "Wise Mentor"
        new_chars.append(primary)
        inherited_names.append(primary.get("name"))
        student_cands = [c for c in all_available if c.get("age_class") in ["Baby", "Juvenile"]]
        student = copy_char(random.choice(student_cands) if student_cands else all_available[0])
        student["role"] = "Eager Student"
        new_chars.append(student)
        introduced_names.append(student.get("name"))

    elif operator == CharacterMutationOperator.PROTECTOR_COMPANION:
        primary = copy_char(p_chars[0]) if p_chars else copy_char(canon_characters[0])
        large_cands = [c for c in all_available if c.get("size_class") in ["Medium", "Large"]]
        protector = copy_char(random.choice(large_cands) if large_cands else all_available[0])
        protector["role"] = "Protective Guardian"
        primary["role"] = "Protected Companion"
        new_chars = [protector, primary]
        inherited_names.append(primary.get("name"))
        introduced_names.append(protector.get("name"))

    elif operator == CharacterMutationOperator.GROUP_CAST:
        # 3 to 4 characters
        new_chars = [copy_char(c) for c in p_chars[:2]]
        for c in new_chars:
            inherited_names.append(c.get("name"))
        while len(new_chars) < 3:
            cand = copy_char(random.choice(all_available))
            if cand.get("name") not in [nc.get("name") for nc in new_chars]:
                cand["role"] = f"Ensemble Member {len(new_chars) + 1}"
                new_chars.append(cand)
                introduced_names.append(cand.get("name"))

    else:
        # Default fallback
        new_chars = [copy_char(c) for c in p_chars]
        inherited_names = list(p_names)

    mutation_metadata = {
        "operator": operator.value,
        "inherited_characters": inherited_names,
        "new_characters": introduced_names,
        "removed_characters": removed_names,
        "total_characters_now": len(new_chars)
    }

    return new_chars, mutation_metadata

def copy_char(char_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to clone a character dictionary."""
    return dict(char_dict)
