#!/usr/bin/env python3
"""
Story Genome and Creative Mutation Matrix for PLB Story Universe Factory
========================================================================
Represents narrative concepts as structured Story Genomes across 20 dimensions.
Drives deep structural mutations across character, relationship, setting, object,
conflict, perspective, twist, and payoff.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
import random

SETTING_VARIATIONS = [
    "Sunlit Backyard Grassy Run with Sprinkler Arena",
    "Rustic Wooden Garden Table under Shady Oak Canopy",
    "Indoor Porch Veranda with Screened Sun Windows",
    "Greenhouse Nursery among Terra Cotta Flower Pots",
    "Early Morning Dewy Meadow with Distant Tree Line",
    "Golden Hour Twilight Barn Ledge with Warm Ambient Glow",
    "Autumn Leaf Mound at the Boundary Fence Line",
    "Cozy Stone Courtyard with Natural Moss Rock Formations",
    "Farm Orchard Ground beside Fallen Apple Baskets",
    "Covered Patio Deck beside Rain Barrel Fountain",
    "Paved Farm Pathway Leading to the Feed Silo",
    "Coop Aviary Runway Covered in Fresh Cedar Shavings",
    "Flowering Vegetable Patch beside Raised Tomato Trellises",
    "Shaded Willow Tree Pond Bank with Floating Water Lilies",
    "Old Red Barn Hayloft Bathed in Dust-Mote Sunbeams",
    "Gravel Driveway Gate Bordering Open Lavender Fields",
    "Sunny Window Sill Nook Piled with Soft Blankets",
    "Wildflower Meadow Pathway near Weathered Beehives",
    "Rustic Tractor Trailer Bed Piled with Golden Straw",
    "Herb Garden Spiral surrounded by Sweet Basil and Mint"
]

TIME_VARIATIONS = [
    "Golden Morning Dawn (First Light Feeding)",
    "Blazing High Noon (Peak Sunlit Standoff)",
    "Late Afternoon Golden Hour (Lazy Shadows)",
    "Twilight Sunset (Approaching Curfew)",
    "Midnight Moonlit Expedition (Forbidden Hours)",
    "Crisp Early Sunrise Mist (Dewdrop Hours)",
    "Breezy Midday Cloudbreak (Spotlight Sun)",
    "Warm Evening Dusk (Fading Crimson Sky)"
]

OBJECT_VARIATIONS = [
    {"name": "Fresh Sliced Green Lime Half", "trait": "Ultra-tart citrus pulp bursting with sour juice"},
    {"name": "Crisp White Horseradish Root", "trait": "Pungent spicy root with intense nasal vapor"},
    {"name": "Chilled Watermelon Wedge", "trait": "Sweet sticky red fruit with slippery black seeds"},
    {"name": "Oscillating Brass Lawn Sprinkler", "trait": "Pressurized mechanical jet emitting rhythmic water bursts"},
    {"name": "Giant Autumn Pumpkin Half", "trait": "Hollowed-out orange cavern with tasty fibrous seeds"},
    {"name": "Melting Strawberry Ice Cube", "trait": "Freezing sweet treat that glides across the table when pushed"},
    {"name": "Crunchy Purple Radish Bulb", "trait": "Peppery spherical vegetable that rolls like a billiard ball"},
    {"name": "Squeaky Yellow Rubber Decoy", "trait": "Inanimate mimic that squeaks with surprising loudness when pecked"},
    {"name": "Cracked Golden Yellow Squash", "trait": "Buttery sweet vegetable with soft fibrous edible curls"},
    {"name": "Fragrant Fresh Mint Bundle", "trait": "Cool aromatic leaves releasing tingling herbal fragrance"},
    {"name": "Frozen Blueberry Sphere", "trait": "Hard frosty orb that rattles across hollow wood like a marble"},
    {"name": "Crinkling Silver Food Wrapper", "trait": "Noisy reflective crinkle foil indicating hidden snacks"},
    {"name": "Polished Green Bell Pepper Cup", "trait": "Crisp hollow vegetable acting like an edible bowl"},
    {"name": "Hollow Cinnamon Bark Roll", "trait": "Dry woody scroll carrying sweet pungent woodland spice"},
    {"name": "Giant Sunflower Blossom Head", "trait": "Massive plate of nutty black-and-white seeds"},
    {"name": "Bouncing Orange Tennis Ball", "trait": "Felted sphere that unpredictably rebounds off surfaces"},
    {"name": "Bubbling Water Basin Fountain", "trait": "Aerated bubbling fountain creating swirling currents"},
    {"name": "Carved Hollow Coconut Shell", "trait": "Rough fibrous brown dome with aromatic white flesh inside"},
    {"name": "Bundle of Crunchy Baby Carrots", "trait": "Snapping orange roots with sweet earth scent"},
    {"name": "Shiny Ceramic Water Bowl", "trait": "Reflective blue dish that doubles as a funhouse mirror"}
]

GOAL_VARIATIONS = [
    "Execute a stealth approach and claim the primary bite before rivals notice",
    "Prove bravery to the rest of the flock by standing firm in front of the mystery object",
    "Retrieve the prized morsel and safely smuggle it to the secret hiding spot",
    "Investigate whether the strange object poses an active threat to companions",
    "Test the culinary texture and acidity like an aristocratic food connoisseur",
    "Break through the sensory fear barrier and enjoy a novel foreign delicacy",
    "Use the distraction created by the object to execute a daring fence hop",
    "Convince an anxious companion that the object is completely safe to examine",
    "Solve the mystery of why the object refuses to move when nudged",
    "Form a cooperative tag-team to dislodge the prize from its resting place",
    "Guard the discovery from encroaching competitors without retreating",
    "Turn the puzzling obstacle into an afternoon amusement park game",
    "Deliver the foreign treasure as an offering to win over a grumpy mentor",
    "Test reflexes against the unexpected rolling movement of the prize",
    "Establish undeniable dominance over the inanimate newcomer in the territory"
]

MOTIVATION_VARIATIONS = [
    "Irresistible curiosity that overrules every survival instinct",
    "Playful one-upmanship against a boasting companion",
    "Fierce loyalty to ensure younger companions do not get startled",
    "Uncontrollable appetite for novel exotic flavors",
    "A desire to be recognized as the undisputed champion of the yard",
    "Boredom transformed into adventurous thrill-seeking",
    "Protective instinct over a beloved nap sanctuary",
    "Curiosity sparked by an unfamiliar sound or shadow",
    "Childlike eagerness to mimic the actions of older animals",
    "The pure pursuit of physical comedy and harmless mischief",
    "Competitive pride triggered by a teasing partner",
    "A secret craving for sweet and crunchy woodland treats"
]

PERSPECTIVE_VARIATIONS = [
    "Third-person cinematic ground-level tracking shot",
    "Close-up first-person animal eye level with heightened sensory details",
    "Sir David Attenborough style solemn wildlife commentator lens",
    "From the perspective of the mystery object observing its curious predators",
    "Human handler watching anxiously through phone camera lens",
    "Wide-angle GoPro mounted at ground level capturing dramatic facial expressions",
    "Overhead drone view framing synchronized stealth movements"
]

TWIST_VARIATIONS = [
    "The formidable object is completely harmless, but a sudden gust of wind rolls it right into the animal",
    "The cautious companion was secretly eating the treat the entire time while the brave leader was hesitating",
    "The recoil knocks over an adjacent prop, revealing an even larger hidden feast beneath it",
    "The two rivals accidentally tackle the object simultaneously, launching it across the yard into the water bowl",
    "The scary sound was not from the object, but from the animal's own tail knocking against a tin bucket",
    "The sour shock gives the animal sudden super-speed zoomies in tight circles",
    "A tiny baby chick strolls up fearlessly and takes a huge bite without batting an eye",
    "The rolling prize hits a garden sprinkler, triggering an instant synchronized shower party",
    "The object splits in half upon impact, creating an exact duplicate problem for both partners",
    "An unexpected partner swoops in with a theatrical leap and claims the victory prize",
    "The creature's intense investigative sniffing accidentally rolls the prize directly under the gate",
    "The supposed treasure turns out to be hollow, acting like a tiny funny helmet for 3 seconds",
    "Both animals freeze in dramatic disbelief as the object rolls backward uphill on its own accord",
    "The terrifying monster obstacle turns out to be their favorite toy missing for two weeks",
    "The loudest critic of the group ends up falling in love with the flavor and refusing to share"
]

PAYOFF_VARIATIONS = [
    "A legendary synchronized head shake and baffled direct gaze straight into the camera lens",
    "A glorious double-shake of fur and feathers followed by an immediate victory nap side-by-side",
    "Mutual laughter across species as both companions realize how silly their panic was",
    "The smallest baby animal casually walks up and devours the prize that terrified the adults",
    "A perfect circular loop where the animal retreats, pauses, and immediately comes right back for more",
    "A triumphant victory dance of hops, head-bobs, and tail-wags celebrating total courage",
    "Both partners share the prize harmoniously after realizing neither can finish it alone",
    "The hero creature smugly accepts affectionate praise from the entire gathered enclosure",
    "An accidental domino collapse of garden pots ends with everyone eating fallen berries happily",
    "A hilarious dramatic sneeze that sends feathers fluttering in slow-motion comedy glory"
]

@dataclass
class StoryGenome:
    story_id: str
    parent_id: str
    generation: int
    world_id: str
    world_name: str
    title: str
    one_line_premise: str
    hook: str
    characters: List[Dict[str, Any]]
    relationships: Dict[str, Any]
    setting: str
    time: str
    objects: List[Dict[str, Any]]
    goal: str
    motivation: str
    conflict: str
    obstacle: str
    action: str
    escalation: str
    emotion: str
    tone: str
    perspective: str
    twist: str
    payoff: str
    loop: str
    evidence_refs: List[str]
    creative_elements: List[str]
    diversity_score: float = 0.75
    quality_score: float = 85.0
    evolution_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryGenome":
        return cls(**data)

def build_root_genome(
    story_dna: Dict[str, Any],
    characters: List[Dict[str, Any]],
    relationships: Dict[str, Any],
    world: Dict[str, Any],
    story_idx: int = 1
) -> StoryGenome:
    """
    Constructs an initial canonical Root Story Genome from Video DNA.
    """
    story_id = f"UNIV-{story_idx:04d}"
    lead_name = characters[0]["name"] if characters else "Protagonist"
    partner_name = characters[1]["name"] if len(characters) > 1 else ""
    clean_set = story_dna.get("setting", "The Setting").split(" / ")[0].strip()
    title = f"{w_name}: {lead_name}{f' & {partner_name}' if partner_name else ''} in {clean_set}"
    premise = story_dna.get("core_premise", "An animal explores a mysterious object.")

    obj_name = story_dna.get("objects", [{}])[0].get("name", "Mystery Object") if story_dna.get("objects") else "Interactive Object"
    if any(tok in obj_name.lower() for tok in ["focal element", "target object", "foreground interactive object"]):
        obj_name = "Interactive Object"

    return StoryGenome(
        story_id=story_id,
        parent_id="ROOT",
        generation=1,
        world_id=world.get("id", "WORLD-01"),
        world_name=world.get("name", "ANIMAL_COMEDY"),
        title=title,
        one_line_premise=premise,
        hook=story_dna.get("hook", f"Within 3 seconds: {lead_name} discovers {obj_name}."),
        characters=characters,
        relationships=relationships,
        setting=story_dna.get("setting", "Garden Run"),
        time="Golden Hour Twilight",
        objects=[{"name": obj_name, "trait": "Observed in source footage"}],
        goal=story_dna.get("conflict", "Investigate and test the object"),
        motivation=story_dna.get("central_tension", "Curiosity vs natural caution"),
        conflict=story_dna.get("conflict", "Hesitation before decisive encounter"),
        obstacle="Cautious instinct and physical distance",
        action="Stealth advance -> Visual lock -> Decisive contact",
        escalation="Step-by-step approach building tension",
        emotion="High curiosity and comedic anticipation",
        tone=world.get("tone", "Playful & Suspenseful"),
        perspective="Third-person ground-level tracking shot",
        twist=story_dna.get("twist", "A surprise sensory reaction"),
        payoff=story_dna.get("payoff", "Comedic expressive recoil and resolution"),
        loop="Loop trigger: subject resets to starting curiosity state for infinite playback.",
        evidence_refs=story_dna.get("evidence_refs", ["EV-01"]),
        creative_elements=[world.get("name"), "Canon Timeline Evidence", relationships.get("type", "COMPANION")],
        diversity_score=0.88,
        quality_score=round(random.uniform(88.0, 95.0), 1),
        evolution_metadata={
            "parent_id": "ROOT",
            "generation": 1,
            "changed_dimensions": ["root_instantiation"],
            "novelty_score": 0.85
        }
    )

def mutate_story_genome(
    parent: StoryGenome,
    new_story_id: str,
    mutated_characters: List[Dict[str, Any]],
    mutated_relationships: Dict[str, Any],
    target_world: Optional[Dict[str, Any]] = None,
    dimensional_shifts: Optional[List[str]] = None
) -> Tuple[StoryGenome, Dict[str, Any]]:
    """
    Applies creative mutations across the genome dimensions to produce an evolved child.
    """
    shifts = dimensional_shifts or ["setting", "goal", "twist"]
    world = target_world or {
        "id": parent.world_id,
        "name": parent.world_name,
        "tone": parent.tone,
        "theme": parent.one_line_premise
    }

    # Apply dimensional mutations
    new_setting = random.choice(SETTING_VARIATIONS) if "setting" in shifts else parent.setting
    new_time = random.choice(TIME_VARIATIONS) if "time" in shifts else parent.time
    new_obj_dict = random.choice(OBJECT_VARIATIONS) if "object" in shifts else (
        parent.objects[0] if parent.objects else OBJECT_VARIATIONS[0]
    )
    new_objects = [new_obj_dict]
    new_goal = random.choice(GOAL_VARIATIONS) if "goal" in shifts else parent.goal
    new_motivation = random.choice(MOTIVATION_VARIATIONS) if "motivation" in shifts else parent.motivation
    new_twist = random.choice(TWIST_VARIATIONS) if "twist" in shifts else parent.twist
    new_payoff = random.choice(PAYOFF_VARIATIONS) if "payoff" in shifts else parent.payoff
    new_perspective = random.choice(PERSPECTIVE_VARIATIONS) if "perspective" in shifts else parent.perspective

    lead = mutated_characters[0]["name"] if mutated_characters else "Protagonist"
    partner = mutated_characters[1]["name"] if len(mutated_characters) > 1 else ""

    # Varied Title Templates
    w_clean = world.get('name', 'COMEDY').replace('_', ' ').title()
    obj_clean = new_objects[0]['name']
    setting_tag = new_setting.split()[0]

    title_options = [
        f"{w_clean}: {lead} {f'& {partner}' if partner else ''} and The {obj_clean}",
        f"The Great {obj_clean} Challenge: {lead} {f'& {partner}' if partner else ''}",
        f"When {lead} {f'and {partner}' if partner else ''} Discovered The {obj_clean}",
        f"{lead}'s {w_clean} Encounter with {obj_clean}",
        f"The {setting_tag} Heist: {lead} {f'Feat. {partner}' if partner else ''}",
        f"{lead} vs {obj_clean}: A {w_clean} Tale"
    ]
    new_title = random.choice(title_options)

    # Varied Premise Templates
    premise_options = [
        f"In {new_setting} at {new_time}, {lead} {f'and {partner}' if partner else ''} must {new_goal.lower()}, driven by {new_motivation.lower()}.",
        f"A surprising discovery in {new_setting} forces {lead} {f'and {partner}' if partner else ''} to {new_goal.lower()}, sparking {new_twist.lower()}.",
        f"Driven by {new_motivation.lower()}, {lead} {f'and {partner}' if partner else ''} confront {obj_clean} in {new_setting} to {new_goal.lower()}.",
        f"At {new_time}, {lead} {f'and {partner}' if partner else ''} face a test in {new_setting}: their quest is to {new_goal.lower()}."
    ]
    new_premise = random.choice(premise_options)

    new_hook = f"Within 3 seconds at {new_time}: {lead} locks eyes with {obj_clean} in {new_setting}."
    new_conflict = f"{mutated_relationships.get('description', 'Inter-species dynamic')} complicates the attempt to {new_goal.lower()}."

    # Track Evolution Metadata
    evolution_meta = {
        "parent_id": parent.story_id,
        "child_id": new_story_id,
        "generation": parent.generation + 1,
        "changed_dimensions": list(set(shifts + ["character", "relationship"])),
        "dimensional_shifts": list(shifts),
        "character_changes": [c.get("name") for c in mutated_characters],
        "relationship_changes": mutated_relationships.get("type", "COMPANION"),
        "new_elements": [new_objects[0]["name"], new_setting, new_time],
        "novelty_score": round(random.uniform(0.74, 0.96), 2)
    }

    child_genome = StoryGenome(
        story_id=new_story_id,
        parent_id=parent.story_id,
        generation=parent.generation + 1,
        world_id=world.get("id", parent.world_id),
        world_name=world.get("name", parent.world_name),
        title=new_title,
        one_line_premise=new_premise,
        hook=new_hook,
        characters=mutated_characters,
        relationships=mutated_relationships,
        setting=new_setting,
        time=new_time,
        objects=new_objects,
        goal=new_goal,
        motivation=new_motivation,
        conflict=new_conflict,
        obstacle=f"Resistance caused by {new_objects[0]['name']}",
        action=f"Stealth approach through {new_setting} -> Encounter -> Climax",
        escalation=f"Initial discovery -> Resistance -> {new_twist}",
        emotion=f"High {world.get('name')} intensity",
        tone=world.get("tone", parent.tone),
        perspective=new_perspective,
        twist=new_twist,
        payoff=new_payoff,
        loop="Seamless loop: ending state naturally resets the opening curiosity.",
        evidence_refs=parent.evidence_refs,
        creative_elements=[world.get("name"), new_objects[0]["name"], mutated_relationships.get("type", "COMPANION")],
        diversity_score=0.85,
        quality_score=round(random.uniform(86.0, 96.0), 1),
        evolution_metadata=evolution_meta
    )

    return child_genome, evolution_meta
