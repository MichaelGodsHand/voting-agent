# knowledge.py
from hyperon import MeTTa, E, S, ValueAtom

def initialize_knowledge_graph(metta: MeTTa):
    """Initialize the MeTTa knowledge graph with voting question data structure."""
    # Brand relationships
    metta.space().add_atom(E(S("brand_has"), S("brand"), S("negative_reviews")))
    metta.space().add_atom(E(S("brand_has"), S("brand"), S("negative_reddit")))
    metta.space().add_atom(E(S("brand_has"), S("brand"), S("negative_social")))
    
    # Voting question relationships
    metta.space().add_atom(E(S("generates_voting_question"), S("negative_feedback"), S("voting_question")))
    metta.space().add_atom(E(S("voting_question_type"), S("voting_question"), S("yes_no")))
    metta.space().add_atom(E(S("voting_question_type"), S("voting_question"), S("multiple_choice")))
    
    # FAQ entries for voting question generation
    metta.space().add_atom(E(S("faq"), S("Hi"), ValueAtom("Hello! I'm your voting question generator. I can help you create voting questions based on negative customer feedback!")))
    metta.space().add_atom(E(S("faq"), S("What brands do you have negative data for?"), ValueAtom("I can query our knowledge graph to find all available brands with negative feedback data. Would you like me to check?")))
    metta.space().add_atom(E(S("faq"), S("How do I generate voting questions?"), ValueAtom("Just ask me to create voting questions for any brand! I'll analyze negative feedback and generate actionable voting questions.")))
    metta.space().add_atom(E(S("faq"), S("What types of voting questions can you create?"), ValueAtom("I can create yes/no questions and multiple choice questions based on negative reviews, Reddit discussions, and social media comments.")))
