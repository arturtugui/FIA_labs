from production import IF, AND, THEN, OR

FLAG_RULES = (

    IF( AND("(?x) is small cross", "(?x) is bicolor"),
        THEN("(?x) is small cross and bicolor") ),    # R1

    IF( AND("(?x) is small cross and bicolor", "(?x) is centered cross"),
        THEN("(?x) is Switzerland") ),                # R2

    IF( AND("(?x) is small cross and bicolor", "(?x) is off-center cross"),
        THEN("(?x) is Greece") ),                     # R3

    IF( OR("(?x) is small cross", "(?x) is off-center cross"),
        THEN("(?x) is small cross or off-center cross") ),  # R4

    IF( AND("(?x) is small cross or off-center cross", "(?x) has stripes"),
        THEN("(?x) is Greece") ),                     # R5

    IF( AND("(?x) is big cross", "(?x) is not outlined cross"),
        THEN("(?x) is big cross and not outlined cross") ),  # R6

    IF( OR("(?x) is big cross and not outlined cross", "(?x) is bicolor"),
        THEN("(?x) is big cross and not outlined cross or bicolor") ),  # R7

    IF( AND("(?x) is big cross and not outlined cross or bicolor", "(?x) is off-center cross"),
        THEN("(?x) is big cross and not outlined cross or bicolor and off-center cross") ),  # R8

    IF( AND("(?x) is big cross and not outlined cross or bicolor and off-center cross", "(?x) is yellow cross"),
        THEN("(?x) is Sweden") ),                     # R9

    IF( AND("(?x) is big cross and not outlined cross or bicolor and off-center cross", "(?x) is blue cross"),
        THEN("(?x) is Finland") ),                    # R10

    IF( AND("(?x) is outlined cross", "(?x) is big cross"),
        THEN("(?x) is outlined cross and big cross") ),  # R11

    IF( OR("(?x) is outlined cross and big cross", "(?x) is tricolor"),
        THEN("(?x) is outlined cross and big cross or tricolor") ),  # R12

    IF( AND("(?x) is outlined cross and big cross or tricolor", "(?x) is off-center cross"),
        THEN("(?x) is outlined cross and big cross or tricolor and off-center cross") ),  # R13

    IF( AND("(?x) is outlined cross and big cross or tricolor and off-center cross", "(?x) is blue cross"),
        THEN("(?x) is Norway") ),                     # R14

    IF( AND("(?x) is outlined cross and big cross or tricolor and off-center cross", "(?x) is red cross"),
        THEN("(?x) is Iceland") ),                    # R15
)

#Switzerland
# FLAG_DATA = (
#     'flag is small cross',
#     'flag is bicolor',
#     'flag is centered cross'
# )

#Greece
# FLAG_DATA = (
#     'flag is small cross',
#     'flag has stripes',
#     'flag is off-center cross',
# )

#Sweden
FLAG_DATA = (
     'flag is bicolor',
     'flag is off-center cross',
     'flag is yellow cross'
 )

#Template
# FLAG_DATA = (
#     'flag is small cross',
#     'flag is bicolor',
#     'flag is centered cross',
#     'flag is off-center cross',
#     'flag has stripes',
#     'flag is big cross',
#     'flag is not outlined cross',
#     'flag is yellow cross',
#     'flag is blue cross',
#     'flag is outlined cross',
#     'flag is tricolor',
#     'flag is red cross',
# )
