#!/usr/bin/env python3
"""
Story Worlds Engine for PLB Story Universe Factory
===================================================
Establishes 15 distinct thematic Story Worlds to categorize,
generate, and cross-pollinate narrative arcs from a single video asset.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List

@dataclass
class StoryWorld:
    id: str
    name: str
    theme: str
    tone: str
    setting_rules: str
    narrative_stakes: str
    pacing: str
    typical_conflicts: List[str] = field(default_factory=list)
    payoff_style: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

CANONICAL_STORY_WORLDS: List[StoryWorld] = [
    StoryWorld(
        id="WORLD-01",
        name="ANIMAL_COMEDY",
        theme="Slapstick Pet Shenanigans & Unfiltered Reactions",
        tone="Lighthearted & High Energy",
        setting_rules="Familiar rustic yards, feeding ledges, sunny patios",
        narrative_stakes="Dignity vs. hilarious loss of composure",
        pacing="Rapid setup -> explosive kinetic reaction -> freeze frame",
        typical_conflicts=["Sour citrus pulp", "Sprinkler blast", "Slippery wood rail", "Uncooperative gravity"],
        payoff_style="Comedic head shake, startled recoil, or synchronized double-take"
    ),
    StoryWorld(
        id="WORLD-02",
        name="WHOLESOME",
        theme="Gentle Comfort & Interspecies Kindness",
        tone="Warm, Tender, Uplifting",
        setting_rules="Sunlit pastures, cozy straw nests, flower garden verandas",
        narrative_stakes="Ensuring every companion feels loved, fed, and included",
        pacing="Calm, unhurried, rhythmic discovery",
        typical_conflicts=["Fear of missing out", "Shyness in meeting someone new", "Gentle misunderstandings"],
        payoff_style="Nuzzling cheeks, shared feast, peaceful afternoon naps side-by-side"
    ),
    StoryWorld(
        id="WORLD-03",
        name="EMOTIONAL",
        theme="Courage Under Vulnerability & Heartfelt Bonds",
        tone="Poignant, Inspiring, Earnest",
        setting_rules="Dramatic twilight yards, quiet barn corners, dawn horizons",
        narrative_stakes="Finding belonging, proving worth to the pack",
        pacing="Slow build with poignant musical beat drops",
        typical_conflicts=["Self-doubt", "Physical clumsiness", "Feeling too small to make a difference"],
        payoff_style="Tearjerker triumph where the underdog earns unconditional respect"
    ),
    StoryWorld(
        id="WORLD-04",
        name="CHAOTIC",
        theme="Exponential Chain Reactions & Farmyard Pandemonium",
        tone="Frenetic, Over-The-Top, Slapstick Farce",
        setting_rules="Rube Goldberg obstacle courses across barns and runs",
        narrative_stakes="Trying to stop the domino collapse before the human handler arrives",
        pacing="Zero to 100 mph in 3 seconds",
        typical_conflicts=["Falling buckets", "Spilled apples", "Tangled leashes", "Runaway sprinklers"],
        payoff_style="Everyone covered in mud/feathers looking around in utter bewilderment"
    ),
    StoryWorld(
        id="WORLD-05",
        name="MYSTERY",
        theme="Backyard Whodunits & The Case of the Missing Snack",
        tone="Noir Satire, Intrigued, Suspenseful",
        setting_rules="Shadowy barn beams, damp stone crawlspaces, moonlit perches",
        narrative_stakes="Unmasking the sneaky thief who stole the prize",
        pacing="Clue gathering -> tension pause -> dramatic reveal",
        typical_conflicts=["Missing footprints", "False leads", "Alibi interrogation among companions"],
        payoff_style="The lead detective turns out to be the one who ate the prize while sleepwalking"
    ),
    StoryWorld(
        id="WORLD-06",
        name="ADVENTURE",
        theme="Epic Backyard Odysseys & Crossing the Forbidden Fence",
        tone="Grand, Cinematic, Heroic",
        setting_rules="Territories expanding beyond the safety fence into neighbor's orchard",
        narrative_stakes="Retrieving the sacred golden food relic for the community",
        pacing="Stealth approach -> high-risk traverse -> daring sprint home",
        typical_conflicts=["Hostile lawn mowers", "The neighborhood sleeping watchdog", "Towering stone walls"],
        payoff_style="Triumphant return with the spoils celebrated like kings"
    ),
    StoryWorld(
        id="WORLD-07",
        name="DOCUMENTARY",
        theme="Dry-Witted Nature Mockumentary & Evolutionary Parody",
        tone="Solemn, Deadpan, Educational Satire",
        setting_rules="Framed with professional telephoto observation distances",
        narrative_stakes="Documenting the rare and elusive apex pet behavior",
        pacing="Slow panning shots with whispering voiceover pauses",
        typical_conflicts=["The subject completely ignoring scientific instincts", "Derpy facial expressions"],
        payoff_style="Narrator's sigh of resignation at the limits of biological majesty"
    ),
    StoryWorld(
        id="WORLD-08",
        name="RIVALRY",
        theme="High-Noon Territory Duels & Turf Showdowns",
        tone="Intense, Snarky, Competitive",
        setting_rules="The exact center of the table, the topmost perch rail",
        narrative_stakes="Sole undisputed sovereignty over the prime resting spot",
        pacing="Stare-down silence -> explosive simultaneous dash",
        typical_conflicts=["Refusing to blink", "Chest bumping", "Mirroring each other's aggressive poses"],
        payoff_style="Both rivals get startled by a third bystander and lose the spot entirely"
    ),
    StoryWorld(
        id="WORLD-09",
        name="FRIENDSHIP",
        theme="Dynamic Duo Shenanigans & Synchronized Escapades",
        tone="Joyful, Upbeat, Inseparable",
        setting_rules="Open grassy fields, water sprinkler arenas, sunny deck stairs",
        narrative_stakes="Showing the world that two different species can conquer anything together",
        pacing="Bouncy, energetic, collaborative flow",
        typical_conflicts=["Coordinating different speeds", "One wanting to swim while other hates water"],
        payoff_style="Synchronized celebrations, high-five paws, mutual ear-grooming"
    ),
    StoryWorld(
        id="WORLD-10",
        name="FAMILY",
        theme="Generational Legacy & Sibling Mayhem",
        tone="Relatable, Messy, Heartwarming",
        setting_rules="Multi-generational coop runs and rabbit warrens",
        narrative_stakes="Teaching the young generation the sacred rules of the yard",
        pacing="Nostalgic storytelling colliding with toddler chaos",
        typical_conflicts=["Young ones wandering off", "Copying forbidden grown-up antics"],
        payoff_style="Exhausted parents watching their rascals curl up together in sleep"
    ),
    StoryWorld(
        id="WORLD-11",
        name="SURPRISE",
        theme="Expectation Inversion & Twist Thrills",
        tone="Shocking, Playful, Unpredictable",
        setting_rules="Ordinary mundane corners hiding astonishing mechanical traps",
        narrative_stakes="What happens when a peaceful routine goes radically sideways in one frame",
        pacing="Deceptive stillness -> sudden 0.5s eruption -> hilarious aftermath",
        typical_conflicts=["Triggering hidden sprinkler jets", "The object suddenly rolling on its own"],
        payoff_style="Jaw-dropping freeze-frame of astonished pet eyes"
    ),
    StoryWorld(
        id="WORLD-12",
        name="TASTE_TEST",
        theme="Pretentious Gourmet Reviews of Bizarre Yard Findings",
        tone="Satirical, Pompous, Sensory Drama",
        setting_rules="Rustic wooden tasting tables under bright overhead sunlight",
        narrative_stakes="Delivering an honest culinary critique of sour citrus or spicy roots",
        pacing="Methodical olfactory inspection -> hesitant nibble -> explosive shock wave",
        typical_conflicts=["Extreme sour acidity", "Pungent nose burn", "Overwhelming tongue tingles"],
        payoff_style="Dignified food critic turning inside out with a frantic head shake"
    ),
    StoryWorld(
        id="WORLD-13",
        name="DISCOVERY",
        theme="Wonderment & The Magic of Unfamiliar Objects",
        tone="Mystical, Enchanted, Awe-Inspiring",
        setting_rules="Sun-dappled glades where garden artifacts appear like alien totems",
        narrative_stakes="Understanding what the strange object wants from the world",
        pacing="Ethereal, ambient, visual focus on lighting and reflections",
        typical_conflicts=["Unfamiliar physical properties", "The mystery of why it smells so different"],
        payoff_style="A moment of cosmic realization and quiet acceptance"
    ),
    StoryWorld(
        id="WORLD-14",
        name="MISUNDERSTANDING",
        theme="Diplomatic Comedy of Errors Across Species",
        tone="Farce, Frantic, Well-Intentioned Blunders",
        setting_rules="Boundary fences where distinct animal enclosures meet",
        narrative_stakes="Preventing a harmless misunderstanding from starting a barnyard war",
        pacing="Rapid escalation based on misread body language",
        typical_conflicts=["Quacks misinterpreted as insults", "Friendly nudges seen as attacks"],
        payoff_style="Realizing the mistake and bursting into collective species laughter"
    ),
    StoryWorld(
        id="WORLD-15",
        name="ROLE_REVERSAL",
        theme="The Small Protect The Big & Underdogs Take The Lead",
        tone="Empowering, Ironic, Delightful",
        setting_rules="Arena settings where size differences are starkly highlighted",
        narrative_stakes="Challenging conventional hierarchy and expectations",
        pacing="Steady role inversion culminating in an unexpected showdown",
        typical_conflicts=["Large guardian cowering while tiny chick/duckling steps forward"],
        payoff_style="The smallest animal in the yard walking like a 10-foot giant"
    )
]

def get_all_story_worlds() -> List[Dict[str, Any]]:
    """Returns all 15 Story Worlds."""
    return [w.to_dict() for w in CANONICAL_STORY_WORLDS]

def get_story_world_by_id(world_id: str) -> StoryWorld:
    """Finds a specific world by ID or name."""
    for w in CANONICAL_STORY_WORLDS:
        if w.id == world_id or w.name.upper() == world_id.upper():
            return w
    return CANONICAL_STORY_WORLDS[0]
