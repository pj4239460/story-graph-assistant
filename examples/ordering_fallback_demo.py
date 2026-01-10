"""
Demo: Ordering Constraints and Fallback Storylets (v1.7.1)

This demonstrates the new features:
1. Ordering constraints (requires_fired, forbids_fired)
2. Fallback storylets when world gets stuck
3. Idle tick tracking
"""
from src.models.project import Project
from src.models.world import WorldState, Effect
from src.models.character import Character
from src.models.storylet import Storylet, Precondition, DirectorConfig
from src.models.scene import Scene
from src.models.world import StoryThread, ThreadStep
from src.services.director_service import DirectorService


def create_demo_project():
    """Create a demo project showing ordering and fallback"""
    return Project(
        id="ordering-fallback-demo",
        name="Ordering & Fallback Demo",
        worldState=WorldState(vars={
            "quest_active": False,
            "player_reputation": 0
        }),
        characters={
            "player": Character(id="player", name="Player"),
            "knight": Character(id="knight", name="Sir Roland")
        },
        scenes={
            "start": Scene(id="start", title="Village Square")
        },
        threads={
            "main": StoryThread(
                id="main",
                name="Main Story",
                steps=[ThreadStep(sceneId="start")]
            )
        },
        storylets={
            # Quest chain with ordering constraints
            "quest_offer": Storylet(
                id="quest_offer",
                title="The Knight's Request",
                description="A knight offers you a quest",
                tags=["quest", "intro"],
                preconditions=[
                    Precondition(path="world.vars.quest_active", op="==", value=False)
                ],
                effects=[
                    Effect(scope="world", target="main", op="set", path="quest_active", value=True)
                ],
                weight=2.0,
                once=True,
                intensity_delta=0.2
            ),
            
            "quest_progress": Storylet(
                id="quest_progress",
                title="On the Quest Path",
                description="You make progress on the quest",
                tags=["quest", "action"],
                preconditions=[
                    Precondition(path="world.vars.quest_active", op="==", value=True)
                ],
                requires_fired=["quest_offer"],  # Must accept quest first
                effects=[
                    Effect(scope="world", target="main", op="add", path="player_reputation", value=10)
                ],
                weight=1.5,
                once=True,
                intensity_delta=0.3
            ),
            
            "quest_complete": Storylet(
                id="quest_complete",
                title="Quest Complete!",
                description="You complete the quest successfully",
                tags=["quest", "reward"],
                preconditions=[
                    Precondition(path="world.vars.quest_active", op="==", value=True),
                    Precondition(path="world.vars.player_reputation", op=">=", value=10)
                ],
                requires_fired=["quest_offer", "quest_progress"],  # Needs both steps
                effects=[
                    Effect(scope="world", target="main", op="set", path="quest_active", value=False),
                    Effect(scope="world", target="main", op="add", path="player_reputation", value=50)
                ],
                weight=2.0,
                once=True,
                intensity_delta=-0.3
            ),
            
            "quest_abandon": Storylet(
                id="quest_abandon",
                title="Abandon Quest",
                description="You decide to abandon the quest",
                tags=["quest", "failure"],
                preconditions=[
                    Precondition(path="world.vars.quest_active", op="==", value=True)
                ],
                requires_fired=["quest_offer"],
                forbids_fired=["quest_complete"],  # Can't abandon after completing!
                effects=[
                    Effect(scope="world", target="main", op="set", path="quest_active", value=False)
                ],
                weight=0.5,
                once=True,
                intensity_delta=-0.2
            ),
            
            # Fallback storylets - keep the world moving
            "fallback_weather": Storylet(
                id="fallback_weather",
                title="Weather Changes",
                description="The weather shifts",
                tags=["fallback", "ambient"],
                preconditions=[],
                effects=[],
                is_fallback=True,
                weight=1.0,
                cooldown=3,
                intensity_delta=-0.1
            ),
            
            "fallback_crowd": Storylet(
                id="fallback_crowd",
                title="Crowd Activity",
                description="People go about their business",
                tags=["fallback", "ambient"],
                preconditions=[],
                effects=[],
                is_fallback=True,
                weight=1.0,
                cooldown=3,
                intensity_delta=-0.1
            )
        }
    )


def run_demo():
    """Run the demo and show results"""
    print("=" * 60)
    print("World Director v1.7.1 Demo: Ordering & Fallback")
    print("=" * 60)
    print()
    
    project = create_demo_project()
    director = DirectorService()
    
    # Configure director with fallback enabled
    config = DirectorConfig(
        events_per_tick=1,
        fallback_after_idle_ticks=3,
        pacing_preference="balanced"
    )
    
    print("Configuration:")
    print(f"  - Events per tick: {config.events_per_tick}")
    print(f"  - Fallback after idle ticks: {config.fallback_after_idle_ticks}")
    print()
    
    # Run 10 ticks
    for i in range(10):
        print(f"\n{'='*60}")
        print(f"Tick #{i}")
        print(f"{'='*60}")
        
        # Show current state
        tick_history_key = "tick_history_main"
        if hasattr(project, 'tick_histories') and tick_history_key in project.tick_histories:
            tick_history = project.tick_histories[tick_history_key]
            print(f"Intensity: {tick_history.current_intensity:.2f}")
            print(f"Idle ticks: {tick_history.idle_tick_count}")
            print()
        
        # Run tick
        tick_record = director.tick(project, "main", 0, config)
        
        # Show results
        if tick_record.events:
            for event in tick_record.events:
                is_fallback = "(FALLBACK)" if any(s.is_fallback for s in project.storylets.values() if s.id == event.storylet_id) else ""
                print(f"✓ {event.storylet_title} {is_fallback}")
                
                # Show effects
                if event.applied_effects:
                    for effect in event.applied_effects:
                        print(f"    → {effect['op']} {effect['path']} = {effect['value']}")
        else:
            print("(No events triggered)")
        
        # Show state changes
        if tick_record.state_diff and "world" in tick_record.state_diff:
            print("\nWorld state changes:")
            for key, change in tick_record.state_diff["world"].items():
                print(f"  {key}: {change['before']} → {change['after']}")
    
    print(f"\n{'='*60}")
    print("Demo Complete!")
    print(f"{'='*60}")
    
    # Final summary
    tick_history = project.tick_histories["tick_history_main"]
    print(f"\nTotal ticks: {len(tick_history.ticks)}")
    print(f"Final intensity: {tick_history.current_intensity:.2f}")
    print(f"Storylets triggered: {len(tick_history.triggered_once)}")
    print("\nTriggered storylets:")
    for storylet_id in tick_history.triggered_once.keys():
        storylet = project.storylets[storylet_id]
        print(f"  - {storylet.title}")


if __name__ == "__main__":
    run_demo()
