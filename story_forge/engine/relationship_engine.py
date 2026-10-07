#!/usr/bin/env python3
"""
Relationship Engine for PLB Story Universe Factory
===================================================
Models character relationships as first-class narrative dimensions.
Supports 14 relationship types, dynamic relationship graphs,
and first-class relationship mutation operators.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

class RelationshipType(str, Enum):
    FRIEND = "FRIEND"
    RIVAL = "RIVAL"
    SIBLING = "SIBLING"
    PARENT_CUB = "PARENT_CUB"
    MENTOR_STUDENT = "MENTOR_STUDENT"
    PROTECTOR = "PROTECTOR"
    COMPANION = "COMPANION"
    MISMATCHED_PARTNERS = "MISMATCHED_PARTNERS"
    COMPETITORS = "COMPETITORS"
    CURIOUS_STRANGERS = "CURIOUS_STRANGERS"
    MISCHIEF_PARTNERS = "MISCHIEF_PARTNERS"
    WITNESS = "WITNESS"
    GROUP = "GROUP"
    UNEXPECTED_TEAM = "UNEXPECTED_TEAM"

RELATIONSHIP_DYNAMICS: Dict[str, Dict[str, str]] = {
    RelationshipType.FRIEND.value: {
        "description": "Loyal companions with mutual trust and synchronized reactions.",
        "tension": "Playful teasing and supportive encouragement.",
        "comedic_trigger": "Trying to comfort each other while both suffering the same silly misfortune."
    },
    RelationshipType.RIVAL.value: {
        "description": "Fierce competitors vying for the high ground or first taste.",
        "tension": "Mutual suspicion, constant one-upmanship, and territorial posturing.",
        "comedic_trigger": "Smug gloating immediately cut short by an unexpected recoil."
    },
    RelationshipType.SIBLING.value: {
        "description": "Family bond with affectionate jealousy and relentless mischief.",
        "tension": "Fighting over everything while teaming up against any outsider.",
        "comedic_trigger": "Tattling, shoving, and copying each other's mistakes."
    },
    RelationshipType.PARENT_CUB.value: {
        "description": "Protective elder guiding a wide-eyed baby explorer.",
        "tension": "Keeping the fearless little one out of trouble.",
        "comedic_trigger": "Parent panics while the baby nonchalantly conquers the hazard."
    },
    RelationshipType.MENTOR_STUDENT.value: {
        "description": "Veteran master demonstrating proper form to an eager apprentice.",
        "tension": "Pride in ancient technique vs rookie's chaotic improvisation.",
        "comedic_trigger": "Master's dignified demonstration fails hilariously; student succeeds by tripping."
    },
    RelationshipType.PROTECTOR.value: {
        "description": "Larger, sturdy guardian shielding a smaller timid friend.",
        "tension": "Vigilant defense of a harmless mystery object.",
        "comedic_trigger": "Protector barking at an orange or lime while the friend happily nibbles it."
    },
    RelationshipType.COMPANION.value: {
        "description": "Cozy side-by-side presence sharing space without friction.",
        "tension": "Shared comfort and shared sensory discoveries.",
        "comedic_trigger": "Synchronized head tilts and mirrored blinks to the camera."
    },
    RelationshipType.MISMATCHED_PARTNERS.value: {
        "description": "Radically different species or temperaments paired by circumstance.",
        "tension": "Total miscommunication of movement and vocal styles.",
        "comedic_trigger": "Fast-paced animal rushing while slow turtle / sleepy cat watches bewildered."
    },
    RelationshipType.COMPETITORS.value: {
        "description": "Contestants in an unspoken arena trial with strict rules.",
        "tension": "Racing to complete the challenge without losing dignity.",
        "comedic_trigger": "Photo finish where both crash into the boundary fence."
    },
    RelationshipType.CURIOUS_STRANGERS.value: {
        "description": "Unfamiliar animals encountering each other across neutral ground.",
        "tension": "Tentative sniffing, sudden jump scares, and cautious curiosity.",
        "comedic_trigger": "Simultaneous pop-jump at the exact moment their noses touch."
    },
    RelationshipType.MISCHIEF_PARTNERS.value: {
        "description": "Co-conspirators orchestrating harmless domestic chaos.",
        "tension": "Coordinating complex schemes without thumbs or words.",
        "comedic_trigger": "High-five paw gestures followed by scrambling to look innocent."
    },
    RelationshipType.WITNESS.value: {
        "description": "One active participant and one deadpan passive onlooker.",
        "tension": "Active participant seeks approval; witness provides silent judgment.",
        "comedic_trigger": "Unbroken direct-to-camera stare from the witness while chaos erupts behind."
    },
    RelationshipType.GROUP.value: {
        "description": "Flock / herd collective with hive-mind dynamics.",
        "tension": "Group consensus shifting rapidly based on the loudest panic sneeze.",
        "comedic_trigger": "Domino scattering effect where one flinch clears the entire table."
    },
    RelationshipType.UNEXPECTED_TEAM.value: {
        "description": "Former adversaries uniting to defeat a common sour or wet obstacle.",
        "tension": "Hesitant collaboration and uneasy shared strategies.",
        "comedic_trigger": "Celebrating their combined breakthrough with an awkward high-five."
    }
}

def determine_relationship_for_ensemble(
    characters: List[Dict[str, Any]],
    preferred_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Builds a primary relationship profile for the current character ensemble.
    """
    if len(characters) < 2:
        return {
            "type": RelationshipType.COMPANION.value,
            "description": "Solo explorer in intimate communion with their environment.",
            "tension": "Internal sensory dialogue.",
            "comedic_trigger": "Talking to oneself through head tilts."
        }

    c1 = characters[0]
    c2 = characters[1]

    # Infer relationship if not explicitly specified
    if not preferred_type:
        if c1.get("age_class") == "Adult" and c2.get("age_class") in ["Baby", "Juvenile"]:
            rel_type = RelationshipType.PARENT_CUB.value
        elif c1.get("species") != c2.get("species"):
            rel_type = RelationshipType.MISMATCHED_PARTNERS.value
        elif c1.get("temperament") == c2.get("temperament"):
            rel_type = RelationshipType.FRIEND.value
        else:
            rel_type = RelationshipType.RIVAL.value
    else:
        rel_type = preferred_type

    info = RELATIONSHIP_DYNAMICS.get(rel_type, RELATIONSHIP_DYNAMICS[RelationshipType.FRIEND.value])

    return {
        "type": rel_type,
        "participants": [c1.get("name"), c2.get("name")],
        "description": f"{c1.get('name')} and {c2.get('name')} act as {rel_type.replace('_', ' ').title()}: {info['description']}",
        "tension": info["tension"],
        "tension_level": info["tension"],
        "comedic_trigger": info["comedic_trigger"]
    }

def mutate_relationship(
    parent_rel: Dict[str, Any],
    characters: List[Dict[str, Any]],
    target_type: Optional[str] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Mutates character relationship dynamics into an evolved state.
    """
    current_type = parent_rel.get("type", RelationshipType.FRIEND.value)
    available_types = [t.value for t in RelationshipType if t.value != current_type]
    
    new_type = target_type if target_type else available_types[0]
    new_rel = determine_relationship_for_ensemble(characters, preferred_type=new_type)

    mutation_meta = {
        "prior_relationship": current_type,
        "new_relationship": new_type,
        "relationship_shift": f"Shifted from {current_type} to {new_type}"
    }

    return new_rel, mutation_meta
