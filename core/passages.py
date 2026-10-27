"""
Typing Racer 2D - Engaging Racing & High-Speed Passages for all Difficulty Levels
"""
import random

PASSAGES = {
    "Easy": [
        "Speed has never killed anyone. Suddenly becoming stationary, that is what gets you. Keep your eyes on the road ahead and accelerate.",
        "The engine roars as the green flag drops. Five cars surge across the starting grid in a burst of speed and burning rubber.",
        "Victory belongs to those who trust their instincts. Shift gears smoothly, hold the racing line, and never lift off the throttle.",
        "Tires grip the asphalt as the straight opens up. Every keystroke fuels your engine toward the finish line ahead.",
        "Focus on the road and find your rhythm. Smooth inputs make fast lap times when every split second counts."
    ],
    "Medium": [
        "In racing, there are moments where everything aligns into pure concentration. The track narrows, the rev limiter screams in top gear, and the blurred horizon rushes toward your windshield. You do not think about shifting or steering; your hands and instincts react before conscious thought can intervene.",
        "A true racing driver does not see corners as obstacles, but as golden opportunities to overtake. Braking late into the apex requires absolute confidence in your mechanical grip. As the car pivots gracefully toward the exit, punch the throttle and unleash every horsepower the engine can muster.",
        "The digital dashboard flickers with vital telemetry. Oil pressure is steady, tire temperatures have reached optimum operating window, and the turbocharger is spinning at maximum boost. Behind you, the chasing pack hunts in your slipstream, searching desperately for any minor slip or error.",
        "Motorsport is a delicate balance between mechanical engineering and human courage. Thousands of precision components work in total harmony to propel a lightweight chassis across asphalt at blistering velocities. Precision at the controls is what transforms raw speed into legendary triumph."
    ],
    "Hard": [
        "The evening light casts long amber shadows across the asphalt as the final stint begins. Through the sweeping Esses, aerodynamic downforce glues the car to the tarmac with immense force, pulling lateral Gs that test the driver's endurance. Behind the dark tinted visor, pupils dilate to track braking markers flashing past at two hundred kilometers per hour. A brief tap on the ceramic brakes transfers weight to the nose, allowing the front tires to bite cleanly before full acceleration unleashes a crescendo of cylinder combustion that echoes through the grandstands.",
        "Precision in competitive racing demands an unyielding calm amidst mechanical fury. Every vibration transmitting through the carbon fiber chassis tells an intricate story: the exact micro-slip of the rear tires, the rumble of aggressive curb strikes, and the subtle aerodynamic turbulence created by competitors ahead. To overtake, one must calculate the closing speed within fractions of a meter, swing out from the aerodynamic draft, and claim the inside line before the next apex closes shut forever.",
        "Night falls over the circuit as twin xenon headlights slice through cool mountain air. The race track is alive with sensory overload: glowing brake discs incandescent orange in the heavy braking zones, the pungent scent of high-octane racing fuel and scorching compound rubber, and the relentless ticking of the timing transponder registering split sectors with ruthless digital certainty."
    ],
    "Extreme Hard": [
        "The championship decider enters its climactic lap under floodlit skies. With throttle pinned wide open through the high-speed banked carousel, the twin-turbocharged V8 engine produces a deafening 850 horsepower symphony at nine thousand RPM. Aerodynamic vortices swirl violently from the rear wing endplates, destabilizing any opponent brave enough to attempt a late slipstream dive. Heart rate surges beyond one hundred and seventy beats per minute, yet your fingers operate the sequential paddle shifters with surgical, clockwork calmness. Every millisecond surrendered to hesitation or an erratic keystroke is an invitation for the chasing pack to steal the lead before the checkered flag falls. Grip the wheel, maintain laser precision, and drive into motorsport immortality.",
        "Under relentless rain and treacherous standing water, the legendary street circuit transforms into a glistening gauntlet of steel barriers and painted white lines. Hydroplaning lurks beneath every throttle application; the slightest over-correction will send two million dollars of bespoke carbon composite chassis spinning into the unforgiving retaining walls. The telemetry engineer crackles through the radio headset, confirming that gap delta to second place is shrinking by three tenths of a second per sector. You must balance the edge of adhesion with unflinching courage: feathering throttle inputs, anticipating sudden camber shifts, and navigating blind apexes where hesitation equates to instant defeat. Push beyond standard human reflexes and conquer the impossible."
    ]
}


def get_random_passage(difficulty: str) -> str:
    """Returns a random passage for the specified difficulty level."""
    pool = PASSAGES.get(difficulty, PASSAGES["Easy"])
    return random.choice(pool)
