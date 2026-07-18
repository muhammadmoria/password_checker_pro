"""Secure password and passphrase generators."""
import secrets
import string
import logging

logger = logging.getLogger(__name__)

# EFF-style word list for passphrase generation
WORDLIST = [
    "abandon", "ability", "abstract", "accept", "access", "account", "achieve",
    "acoustic", "action", "adjust", "admire", "admit", "advance", "advice",
    "agency", "agenda", "almost", "always", "amazing", "analyze", "anchor",
    "animal", "annual", "answer", "apart", "appeal", "apple", "apply",
    "approve", "arch", "arctic", "area", "argue", "armed", "armor",
    "army", "around", "arrange", "arrest", "arrive", "arrow", "article",
    "artist", "aspect", "assault", "assist", "assume", "athlete", "atom",
    "attack", "attend", "attitude", "attract", "auction", "audit", "august",
    "author", "autumn", "avenue", "average", "avoid", "award", "aware",
    "balance", "ballot", "banana", "banner", "barrel", "basic", "basket",
    "battle", "beauty", "become", "beyond", "bicycle", "binary", "biology",
    "bishop", "border", "bottle", "bottom", "bounce", "branch", "bridge",
    "bright", "broken", "bronze", "bubble", "budget", "burden", "butter",
    "cabin", "cable", "cactus", "camera", "campus", "candle", "canoe",
    "canvas", "carbon", "career", "castle", "casual", "cattle", "cement",
    "chain", "chamber", "chance", "change", "channel", "chapter", "charge",
    "cheese", "cherry", "chess", "chicken", "circuit", "citizen", "clarify",
    "classic", "climate", "clock", "close", "cloud", "cluster", "coast",
    "cobra", "coffee", "comedy", "comfort", "common", "compass", "concert",
    "confirm", "connect", "consist", "control", "convert", "cookie", "coral",
    "corner", "cosmic", "cotton", "courage", "cradle", "crash", "crazy",
    "cream", "create", "credit", "cricket", "crime", "crisp", "cross",
    "crowd", "crown", "crucial", "cruel", "cruise", "crumble", "crunch",
    "crystal", "cubic", "curious", "current", "curtain", "cushion", "custom",
    "damage", "daring", "darkness", "daughter", "dazzle", "debate", "decade",
    "decimal", "decide", "declare", "decorate", "define", "degree", "deliver",
    "demand", "depth", "design", "desire", "detail", "detect", "develop",
    "diamond", "diary", "dignity", "dilemma", "dinner", "direct", "disco",
    "discuss", "disease", "display", "distant", "divert", "divorce", "doctor",
    "dolphin", "domain", "double", "dragon", "drama", "drift", "drink",
    "drive", "drop", "drum", "duck", "duration", "dutch", "dwarf",
    "dynamic", "eager", "eagle", "early", "earth", "east", "echo",
    "ecology", "edge", "edit", "educate", "effect", "effort", "either",
    "elastic", "elbow", "elder", "elite", "embody", "emerge", "emotion",
    "empire", "employ", "empty", "enable", "energy", "engage", "engine",
    "enjoy", "enrich", "ensure", "enter", "entire", "envoy", "equal",
    "equip", "error", "escape", "estate", "eternal", "evaluate", "evening",
    "event", "evidence", "evil", "exact", "example", "excel", "except",
    "exchange", "excite", "exclude", "excuse", "execute", "exercise", "exhaust",
    "exotic", "expand", "expect", "expert", "expire", "explain", "explore",
    "express", "extend", "extra", "fabric", "factual", "falcon", "family",
    "famous", "fantasy", "fashion", "father", "fatigue", "fault", "favorite",
    "feature", "federal", "fellow", "female", "fence", "festival", "fetch",
    "fever", "fiber", "fiction", "field", "fifteen", "figure", "filter",
    "final", "finance", "finger", "finish", "firm", "fiscal", "flag",
    "flame", "flash", "flat", "flavor", "fleet", "flesh", "flight",
    "float", "flood", "floor", "flour", "flower", "fluid", "flush",
    "focus", "foliage", "follow", "forbid", "forest", "forget", "formal",
    "format", "former", "fossil", "foster", "fountain", "fragile", "frame",
    "freedom", "freeze", "fresh", "friend", "frozen", "fruit", "fuel",
    "funny", "furnace", "fury", "future", "gadget", "galaxy", "gallery",
    "garage", "garden", "garlic", "garment", "gather", "gauge", "gazelle",
    "gender", "general", "genius", "genuine", "geometry", "germ", "ghost",
    "giant", "gift", "ginger", "giraffe", "girl", "glad", "glance",
    "glare", "glass", "glide", "gloom", "glory", "glove", "glow",
    "glue", "goblin", "golden", "goose", "gospel", "gossip", "govern",
    "grace", "grain", "grand", "grant", "grape", "graph", "grasp",
    "grass", "gravity", "great", "green", "grid", "grief", "grit",
    "group", "grove", "grown", "guard", "guess", "guide", "guilt",
    "guitar", "gulf", "guru", "habit", "half", "hammer", "handle",
    "happy", "harbor", "harden", "harmony", "harvest", "hatch", "hazard",
    "head", "health", "heart", "heavy", "helmet", "help", "herald",
    "hero", "hidden", "hierarchy", "high", "hike", "history", "hobby",
    "hockey", "hold", "holiday", "hollow", "holy", "honest", "honor",
    "hope", "horizon", "horn", "horse", "hospital", "host", "hotel",
    "house", "human", "humor", "hundred", "hunger", "hunter", "hybrid",
    "ice", "icon", "ideal", "identify", "idle", "idol", "ignore",
    "illegal", "illness", "image", "imagine", "immense", "impact", "import",
    "improve", "impulse", "income", "indicate", "indoor", "infant", "inform",
    "inhale", "inherit", "initial", "inject", "injure", "inland", "inner",
    "input", "inquire", "insane", "insect", "inside", "inspire", "install",
    "intact", "intent", "invest", "invite", "involve", "iron", "island",
    "isolate", "issue", "itself", "jacket", " jaguar", "jazz", "jealous",
    "jeans", "jelly", "jewel", "joint", "joke", "journey", "joy",
    "judge", "juice", "jumble", "jungle", "junior", "junk", "justify",
    "kangaroo", "keen", "kettle", "key", "kick", "kidney", "kind",
    "king", "kiosk", "kitchen", "kite", "kitten", "knee", "knife",
    "knight", "knock", "known", "koala", "label", "labor", "ladder",
    "lady", "lake", "lamp", "land", "language", "lantern", "lapse",
    "large", "laser", "last", "later", "laugh", "launch", "laundry",
    "lava", "law", "lawyer", "layer", "lazy", "leader", "leaf",
    "league", "leak", "learn", "leather", "leave", "ledge", "legacy",
    "legal", "legend", "lemon", "length", "lens", "leopard", "lesson",
    "letter", "level", "liar", "liberty", "library", "license", "life",
    "light", "likely", "limit", "linear", "liquid", "listen", "little",
    "live", "lizard", "load", "lobster", "local", "lock", "lodge",
    "logic", "lonely", "long", "loop", "lottery", "lounge", "love",
    "loyal", "lucky", "lumber", "lunar", "lunch", "luxury", "lyric",
]


class GeneratorService:
    """Secure password and passphrase generator using the secrets module."""

    def generate_password(
        self,
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_similar: bool = False,
        exclude_ambiguous: bool = False,
    ) -> str:
        """Generate a cryptographically secure random password."""
        if length < 4:
            length = 4
        if length > 128:
            length = 128

        similar_chars = "il1Lo0O"
        ambiguous_chars = "{}[]()/\\\"'`~,;:.<>"

        pools: list[str] = []
        if use_lowercase:
            pool = string.ascii_lowercase
            if exclude_similar:
                pool = "".join(c for c in pool if c not in similar_chars)
            pools.append(pool)
        if use_uppercase:
            pool = string.ascii_uppercase
            if exclude_similar:
                pool = "".join(c for c in pool if c not in similar_chars)
            pools.append(pool)
        if use_digits:
            pool = string.digits
            if exclude_similar:
                pool = "".join(c for c in pool if c not in similar_chars)
            pools.append(pool)
        if use_symbols:
            pool = string.punctuation
            if exclude_ambiguous:
                pool = "".join(c for c in pool if c not in ambiguous_chars)
            pools.append(pool)

        if not pools:
            pools = [string.ascii_lowercase]

        full_pool = "".join(pools)
        if not full_pool:
            full_pool = string.ascii_lowercase

        password_chars: list[str] = []

        # Ensure at least one character from each selected pool
        for pool in pools:
            password_chars.append(secrets.choice(pool))

        # Fill the rest
        remaining = length - len(password_chars)
        for _ in range(remaining):
            password_chars.append(secrets.choice(full_pool))

        # Shuffle securely
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        return "".join(password_chars[:length])

    def generate_passphrase(
        self,
        num_words: int = 4,
        separator: str = "-",
        capitalize: bool = True,
        add_number: bool = True,
        add_symbol: bool = False,
    ) -> str:
        """Generate a memorable passphrase using a word list."""
        if num_words < 2:
            num_words = 2
        if num_words > 12:
            num_words = 12

        words = []
        for _ in range(num_words):
            word = secrets.choice(WORDLIST)
            if capitalize:
                word = word.capitalize()
            words.append(word)

        passphrase = separator.join(words)

        if add_number:
            passphrase += separator + str(secrets.randbelow(10000))

        if add_symbol:
            passphrase += secrets.choice(string.punctuation)

        return passphrase

    def generate_pin(self, length: int = 6) -> str:
        """Generate a numeric PIN."""
        if length < 4:
            length = 4
        if length > 12:
            length = 12
        return "".join(str(secrets.randbelow(10)) for _ in range(length))