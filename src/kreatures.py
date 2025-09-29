# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import random
import time
from world.world import World
from entity.livingEntity import LivingEntity
from config.config import Config


# @author Daniel McCoy Stephenson
class Kreatures:
    def __init__(self):
        self.environment = World()

        self.names = [
            # Original names
            "Jesse",
            "Juan",
            "Jose",
            "Ralph",
            "Jeremy",
            "Bobby",
            "Johnny",
            "Douglas",
            "Peter",
            "Scott",
            "Kyle",
            "Billy",
            "Terry",
            "Randy",
            "Adam",
            # Additional male names
            "Alexander",
            "Andrew",
            "Anthony",
            "Austin",
            "Benjamin",
            "Brandon",
            "Brian",
            "Christopher",
            "Daniel",
            "David",
            "Edward",
            "Ethan",
            "Gabriel",
            "George",
            "Henry",
            "Isaac",
            "Jacob",
            "James",
            "Jason",
            "John",
            "Joseph",
            "Joshua",
            "Kevin",
            "Lucas",
            "Matthew",
            "Michael",
            "Nathan",
            "Nicholas",
            "Oliver",
            "Patrick",
            "Richard",
            "Robert",
            "Samuel",
            "Stephen",
            "Thomas",
            "Timothy",
            "Tyler",
            "William",
            "Zachary",
            # Female names
            "Abigail",
            "Alice",
            "Amanda",
            "Amy",
            "Angela",
            "Anna",
            "Ashley",
            "Barbara",
            "Betty",
            "Brenda",
            "Brittany",
            "Carol",
            "Catherine",
            "Charlotte",
            "Christina",
            "Christine",
            "Deborah",
            "Diana",
            "Donna",
            "Dorothy",
            "Elizabeth",
            "Emily",
            "Emma",
            "Grace",
            "Hannah",
            "Helen",
            "Isabella",
            "Jessica",
            "Jennifer",
            "Julie",
            "Karen",
            "Katherine",
            "Kimberly",
            "Laura",
            "Linda",
            "Lisa",
            "Margaret",
            "Maria",
            "Marie",
            "Mary",
            "Michelle",
            "Nancy",
            "Nicole",
            "Olivia",
            "Patricia",
            "Rachel",
            "Rebecca",
            "Ruth",
            "Sandra",
            "Sarah",
            "Sharon",
            "Sophia",
            "Susan",
            "Victoria",
            # Modern/diverse names
            "Aiden",
            "Aria",
            "Avery",
            "Blake",
            "Caleb",
            "Chloe",
            "Dakota",
            "Elijah",
            "Felix",
            "Harper",
            "Hunter",
            "Ian",
            "Jaxon",
            "Liam",
            "Luna",
            "Madison",
            "Mason",
            "Maya",
            "Mia",
            "Noah",
            "Owen",
            "Parker",
            "Quinn",
            "Riley",
            "Sage",
            "Taylor",
            "Zoe",
            # International names
            "Ahmed",
            "Aiko",
            "Carlos",
            "Chen",
            "Diego",
            "Elena",
            "Giovanni",
            "Hassan",
            "Ivan",
            "Jin",
            "Kai",
            "Lucia",
            "Mohammed",
            "Natasha",
            "Oscar",
            "Pierre",
            "Raj",
            "Sofia",
            "Takeshi",
            "Valentina",
            "Wei",
            "Yuki",
            "Zara",
            # Additional expanded names for doubling
            # Traditional names continued
            "Aaron",
            "Adrian",
            "Adriana",
            "Albert",
            "Alicia",
            "Allen",
            "Allison",
            "Andre",
            "Andrea",
            "Antonio",
            "Ariana",
            "Arthur",
            "Ashton",
            "Aubrey",
            "Audrey",
            "Autumn",
            "Bella",
            "Bernard",
            "Bethany",
            "Beverly",
            "Brandi",
            "Brooke",
            "Bruce",
            "Cameron",
            "Camila",
            "Carl",
            "Carmen",
            "Caroline",
            "Cassandra",
            "Cedric",
            "Celeste",
            "Charles",
            "Chelsea",
            "Chester",
            "Christian",
            "Claire",
            "Clara",
            "Clarence",
            "Claudia",
            "Clayton",
            "Clifford",
            "Colin",
            "Colleen",
            "Cooper",
            "Courtney",
            "Crystal",
            "Curtis",
            "Cynthia",
            "Damian",
            "Dana",
            "Danielle",
            "Darius",
            "Darryl",
            "Dawn",
            "Dean",
            "Debbie",
            "Dennis",
            "Derek",
            "Desiree",
            "Devin",
            "Diane",
            "Dominic",
            "Donovan",
            "Edgar",
            "Edith",
            "Edmund",
            "Eduardo",
            "Edwin",
            "Eleanor",
            "Elias",
            "Ellen",
            "Elsie",
            "Emanuel",
            "Emilia",
            "Eric",
            "Erica",
            "Ernest",
            "Eugene",
            "Eva",
            "Evan",
            "Evelyn",
            "Faith",
            "Fernando",
            "Florence",
            "Floyd",
            "Frances",
            "Francisco",
            "Frank",
            "Frederick",
            "Gabriela",
            "Gareth",
            "Garrett",
            "Geoffrey",
            "Gerald",
            "Gilbert",
            "Gina",
            "Glenn",
            "Gloria",
            "Gordon",
            "Graham",
            "Grant",
            "Gregory",
            "Gwendolyn",
            "Harold",
            "Hazel",
            "Heather",
            "Hector",
            "Herbert",
            "Holly",
            "Howard",
            "Hugo",
            "Iris",
            "Jack",
            "Jackie",
            "Jackson",
            "Jacqueline",
            "Jake",
            "Janet",
            "Javier",
            "Jeffery",
            "Jenna",
            "Jerome",
            "Jillian",
            "Joanna",
            "Joel",
            "Johnathan",
            "Jonah",
            "Jonathan",
            "Jordan",
            "Josiah",
            "Joyce",
            "Judith",
            "Julian",
            "Juliana",
            "Julius",
            "June",
            "Justin",
            "Kaitlyn",
            "Keith",
            "Kelvin",
            "Kenneth",
            "Kent",
            "Kirk",
            "Kristen",
            "Lance",
            "Larry",
            "Lauren",
            "Lawrence",
            "Leah",
            "Leonard",
            "Lillian",
            "Logan",
            "Lorraine",
            "Louis",
            "Louise",
            "Lucy",
            "Luis",
            "Luke",
            "Lydia",
            "Marcus",
            "Marina",
            "Mark",
            "Marshall",
            "Martin",
            "Marvin",
            "Mateo",
            "Maureen",
            "Maurice",
            "Max",
            "Melanie",
            "Melissa",
            "Miguel",
            "Miranda",
            "Mitchell",
            "Monica",
            "Morgan",
            "Natalie",
            "Neil",
            "Nelson",
            "Nora",
            "Norman",
            "Omar",
            "Paige",
            "Paul",
            "Penny",
            "Philip",
            "Phyllis",
            "Preston",
            "Priscilla",
            "Quentin",
            "Raymond",
            "Regina",
            "Reginald",
            "Renee",
            "Ricardo",
            "Rita",
            "Roberto",
            "Robin",
            "Roger",
            "Ronald",
            "Rosa",
            "Rose",
            "Roy",
            "Ruby",
            "Russell",
            "Ryan",
            "Sabrina",
            "Sally",
            "Samantha",
            "Sean",
            "Sebastian",
            "Sergio",
            "Shane",
            "Sheila",
            "Shelby",
            "Shirley",
            "Simon",
            "Stacy",
            "Stanley",
            "Stella",
            "Stephanie",
            "Steve",
            "Steven",
            "Stuart",
            "Tamara",
            "Tanya",
            "Tara",
            "Teresa",
            "Theresa",
            "Todd",
            "Tony",
            "Tracy",
            "Trevor",
            "Troy",
            "Vanessa",
            "Vernon",
            "Victor",
            "Vincent",
            "Virginia",
            "Walter",
            "Warren",
            "Wayne",
            "Wendy",
            "Wesley",
            "Whitney",
        ]

        print("What would you like to name your kreature?")
        self.creatureName = input("> ")
        self.playerCreature = LivingEntity(self.creatureName)

        self.running = True
        self.config = Config()
        self.tick = 0

    def initiateEntityActions(self):
        entities_to_remove = []  # Track entities that die this turn

        for entity in self.environment.getEntities():
            target = self.environment.getRandomEntity()

            if target == entity:
                continue

            decision = entity.getNextAction(target)

            if decision == "nothing":
                entity.log.append(
                    "%s had an argument with %s!" % (entity.name, target.name)
                )
            elif decision == "love":
                parents = entity.reproduce(target)
                entity.increaseChanceToBefriend()
                entity.decreaseChanceToFight()
                self.createChildEntity(parents[0], parents[1])
            elif decision == "fight":
                if target == self.playerCreature and self.config.godMode:
                    continue
                entity.increaseChanceToFight()
                entity.decreaseChanceToBefriend()
                entity.fight(target)
                # Check if either entity died from the fight to the death
                if not target.isAlive() and target not in entities_to_remove:
                    entities_to_remove.append(target)
                if not entity.isAlive() and entity not in entities_to_remove:
                    entities_to_remove.append(entity)
            elif decision == "befriend":
                entity.increaseChanceToBefriend()
                entity.decreaseChanceToFight()
                entity.befriend(target)

        # Remove all entities that died this turn
        for entity in entities_to_remove:
            self.environment.removeEntity(entity)

    def regenerateAllEntities(self):
        """Regenerate health for all living entities"""
        for entity in self.environment.getEntities():
            if entity.isAlive():
                entity.regenerateHealth()

    def createEntity(self):
        newEntity = LivingEntity(self.names[random.randint(0, len(self.names) - 1)])
        self.environment.addEntity(newEntity)

    def createChildEntity(self, parent1, parent2):
        """Create a child entity with proper parent-child relationships"""
        childName = self.names[random.randint(0, len(self.names) - 1)]
        child = LivingEntity(childName)

        # Set up parent-child relationships
        child.addParent(parent1)
        child.addParent(parent2)
        parent1.addChild(child)
        parent2.addChild(child)

        # Child inherits some traits from parents (average)
        child.chanceToFight = (parent1.chanceToFight + parent2.chanceToFight) // 2
        child.chanceToBefriend = 100 - child.chanceToFight

        # Child inherits health traits from parents (average with some variation)
        parentHealthAvg = (parent1.maxHealth + parent2.maxHealth) // 2
        child.health = parentHealthAvg + random.randint(-10, 10)  # Add some variation
        child.maxHealth = child.health

        child.log.append(
            "%s is the child of %s and %s." % (childName, parent1.name, parent2.name)
        )

        self.environment.addEntity(child)
        return child

    def getLivingChildren(self, entity):
        """Get all living children of an entity"""
        living_children = []
        for child in entity.children:
            if child in self.environment.entities:
                living_children.append(child)
        return living_children

    def continueAsChild(self):
        """Allow player to continue as one of their creature's children"""
        living_children = self.getLivingChildren(self.playerCreature)

        if not living_children:
            return False

        print(
            f"\n{self.playerCreature.name} has died, but has {len(living_children)} living children!"
        )
        print("Would you like to continue as one of your children? (y/n)")
        choice = input("> ").lower().strip()

        if choice == "y" or choice == "yes":
            if len(living_children) == 1:
                # Only one child, automatically select it
                new_player = living_children[0]
                print(f"You are now playing as {new_player.name}!")
            else:
                # Multiple children, let player choose
                print("\nWhich child would you like to continue as?")
                for i, child in enumerate(living_children):
                    print(f"{i+1}. {child.name}")

                while True:
                    try:
                        choice_idx = int(input("> ")) - 1
                        if 0 <= choice_idx < len(living_children):
                            new_player = living_children[choice_idx]
                            print(f"You are now playing as {new_player.name}!")
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a number.")

            # Update the player creature reference
            self.playerCreature = new_player
            # Make sure the new player creature is at position 0 in the entities list
            if new_player in self.environment.entities:
                self.environment.entities.remove(new_player)
            self.environment.entities.insert(0, new_player)
            self.running = True  # Continue the game
            return True

        return False

    def printSummary(self):
        print("=== Summary ===")
        if self.playerCreature.chanceToFight > self.playerCreature.chanceToBefriend:
            print("%s was ferocious." % self.playerCreature.name)
        elif self.playerCreature.chanceToBefriend > self.playerCreature.chanceToFight:
            print("%s was very friendly." % self.playerCreature.name)
        else:
            print("%s was neutral." % self.playerCreature.name)
        print(
            "%s's chance to get into a fight was %d percent."
            % (self.playerCreature.name, self.playerCreature.chanceToFight)
        )
        print(
            "%s's chance to be nice was %d percent."
            % (self.playerCreature.name, self.playerCreature.chanceToBefriend)
        )
        if self.playerCreature.isAlive():
            print(
                "%s ended with %d health (out of %d max)."
                % (
                    self.playerCreature.name,
                    self.playerCreature.health,
                    self.playerCreature.maxHealth,
                )
            )
        else:
            print("%s died during the simulation." % self.playerCreature.name)
        print("Kreatures still alive: %d" % self.environment.getNumEntities())

    def printStats(self):
        print("=== Stats ===")
        print("Friendships forged: %d" % self.playerCreature.stats.numFriendshipsForged)
        print("Babies made: %d" % self.playerCreature.stats.numOffspring)
        print("Creatures Eaten: %d" % self.playerCreature.stats.numCreaturesEaten)

    def run(self):
        self.environment.entities[0] = self.playerCreature
        print("")

        # code to run a day, then show any new additions to log
        while self.running:
            try:
                print(self.playerCreature.log[0])  # tries to print log entry
                if (
                    "eaten" in self.playerCreature.log[0]
                ):  # if creature was eaten, check for children
                    if not self.continueAsChild():
                        self.running = False
                        break
                del self.playerCreature.log[0]  # tries to delete log entry
            except:  # if list is empty, just keep going
                pass

            self.initiateEntityActions()
            self.regenerateAllEntities()  # Regenerate health for all entities
            time.sleep(self.config.tickLength)
            self.tick += 1
            if self.tick >= self.config.maxTicks:
                print("Maximum iterations reached.")
                self.running = False
                break

        input("[CONTINUE]")

        self.printSummary()
        self.printStats()


kreatures = Kreatures()
kreatures.run()
