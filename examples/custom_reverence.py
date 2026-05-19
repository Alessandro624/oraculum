"""
Example demonstrating the reverence parameter.

Higher reverence levels append additional honorific titles to the invocation.
This example prints the prayer text so you can see what is actually sent
to the oracle at different reverence levels.
"""

from oraculum.prayers import PrayerBuilder

formula = "(x1 OR x2) AND (NOT x1 OR x3)"

for level in [1, 5, 10]:
    print(f"Reverence level: {level}")
    builder = PrayerBuilder(reverence=level)
    prayer = builder.build_sat_prayer(formula)
    # Print only the first line of the invocation to compare honorifics
    first_line = prayer.split("\n")[0]
    print(first_line)
    print()
