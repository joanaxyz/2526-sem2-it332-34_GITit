STORIES = [
    {
        "slug": "arcane-spire",
        "title": "The Arcane Spire",
        "summary": (
            "A beginner campaign about creating reliable repositories, shaping intentional snapshots, "
            "reading history, branching safely, integrating work, recovering from mistakes, and exchanging "
            "clean history with the Guild Archive."
        ),
        "narrative_brief": {
            "premise": (
                "The Arcane Spire preserves spells, maps, and expedition reports as chains of immutable "
                "memory crystals. A lightning strike has awakened the tower while fracturing its Chronicle "
                "Core, leaving drafts, snapshots, branch paths, and signal mirrors out of agreement."
            ),
            "player_role": (
                "You are a new Chronicle Keeper apprenticed to Archivist Mira. Your work is to decide which "
                "pages belong in each memory, preserve useful history, name important paths, and reconnect "
                "the repaired archive to the distant Guild."
            ),
            "setting": (
                "An ancient magical observatory of scriptoria, branching stairways, memory galleries, "
                "recovery vaults, and long-range signal chambers."
            ),
            "inciting_incident": (
                "The Chronicle Core restarts after the storm and reveals that the tower's current files no "
                "longer form a trustworthy history."
            ),
            "central_problem": (
                "The Spire cannot resume its research until its working rooms, selected pages, sealed "
                "memories, named paths, and Guild copy all describe one understandable project history."
            ),
            "recurring_characters": [
                {
                    "name": "Archivist Mira",
                    "role": "A patient mentor who asks the learner to inspect repository state before acting.",
                },
                {
                    "name": "Pip",
                    "role": "An impulsive apprentice whose believable mistakes create safe undo and recovery lessons.",
                },
                {
                    "name": "Warden Cael",
                    "role": "Keeper of the signal chamber who introduces collaboration and remote constraints.",
                },
            ],
            "stakes": (
                "If the archive is repaired carelessly, future keepers will inherit hidden drafts, misleading "
                "branches, or destructive corrections that make the Chronicle impossible to trust."
            ),
            "chapter_progression": (
                "The learner awakens the repository, selects and records snapshots, protects tracked paths, "
                "reads history, creates parallel branches, integrates them, repairs mistakes, and finally "
                "hands a clean history to the Guild."
            ),
            "resolution": (
                "The Spire's signal chamber exchanges a clean, inspectable history with the Guild Archive. "
                "The learner understands the working tree, index, commits, refs, and remotes as one system."
            ),
            "learning_metaphor": {
                "working_tree": "the room currently being edited",
                "index": "the tray of pages selected for the next record",
                "commit": "a sealed memory crystal",
                "branch": "a named path through the tower's history",
                "remote": "another archive with its own references",
            },
        },
        "price": 0,
        "sort_order": 1,
        "is_published": True,
        "world_slug": "arcane-spire",
        "difficulty": "beginner",
        "prerequisite_story": None,
    },
    {
        "slug": "frostbound-citadel",
        "title": "Frostbound Citadel",
        "summary": (
            "An intermediate winter campaign about coordinating many contributors, shaping patch series, "
            "resolving conflicts, debugging regressions, governing remotes, and delivering auditable releases."
        ),
        "narrative_brief": {
            "premise": (
                "Frostbound Citadel controls the heat relays that keep the northern settlements alive. During "
                "a prolonged whiteout, isolated engineering teams produced competing repairs against different "
                "versions of the relay controller. Their work has reached the Citadel as tangled branches, "
                "partial patches, disputed conflicts, and rewritten histories."
            ),
            "player_role": (
                "You serve as Integration Marshal under Commander Sera Vale. You must preserve each team's "
                "useful work, decide how histories should combine, investigate regressions, and publish a "
                "release that remote stations can trust."
            ),
            "setting": (
                "A winter fortress spanning frozen bridges, forge halls, signal bastions, avalanche tunnels, "
                "and an aurora observatory above the storm line."
            ),
            "inciting_incident": (
                "The primary heat relay fails while three repair convoys arrive with incompatible histories "
                "and no shared account of which change introduced the fault."
            ),
            "central_problem": (
                "The Citadel needs one reviewable, tested branch assembled from divergent work without losing "
                "authorship, overwriting collaborators, or hiding the origin of the regression."
            ),
            "recurring_characters": [
                {
                    "name": "Commander Sera Vale",
                    "role": "The release owner who demands evidence before history is rewritten or published.",
                },
                {
                    "name": "Engineer Torren",
                    "role": "A fast-moving field engineer whose valuable patches often arrive in difficult forms.",
                },
                {
                    "name": "Analyst Niva",
                    "role": "A regression investigator who teaches comparison, bisecting, and release verification.",
                },
            ],
            "stakes": (
                "A wrong merge, unsafe force push, or unverified release can strand settlements without heat "
                "and erase the evidence needed to repair the next failure."
            ),
            "chapter_progression": (
                "The learner reshapes commits, chooses integration strategies, resolves conflicts, transports "
                "patches, rebases review series, governs remotes, hunts a regression, prepares release evidence, "
                "and publishes the repaired controller."
            ),
            "resolution": (
                "A signed and reviewable release reaches every relay station. The Citadel survives the storm, "
                "and its teams adopt a collaboration history that can be audited instead of merely trusted."
            ),
            "learning_metaphor": {
                "branch": "a repair convoy traveling from a shared base",
                "merge": "bringing convoys through one guarded gate",
                "rebase": "moving a repair route onto a newly cleared road",
                "remote_ref": "a signal tower's last confirmed report",
                "release": "a tested heat-core design distributed to every settlement",
            },
        },
        "price": 350,
        "sort_order": 2,
        "is_published": True,
        "world_slug": "frostbound-citadel",
        "difficulty": "intermediate",
        "prerequisite_story": "arcane-spire",
    },
    {
        "slug": "neon-backstreets",
        "title": "Neon Backstreets",
        "summary": (
            "An advanced neon street campaign about repository forensics, large-scale workspaces, automation, "
            "trust, server operations, maintenance, migration, and Git's object machinery."
        ),
        "narrative_brief": {
            "premise": (
                "Neon Backstreets is a dense street district whose shops, clinics, transit stops, and night-market "
                "services are coordinated by thousands of repositories. A cascading deployment incident has left "
                "blocks running different histories while the district archive reports corrupted references and an "
                "untrusted automation chain."
            ),
            "player_role": (
                "You join the Backstreets Reliability Crew as a Repository Systems Engineer. You investigate "
                "history at scale, isolate regressions, manage parallel workspaces, verify trust, restore object "
                "health, operate synchronization services, and migrate history without losing identity."
            ),
            "setting": (
                "A neon district of ramen stalls, corner shops, transit alleys, workshop rooftops, security "
                "kiosks, signal relays, and basement archive rooms."
            ),
            "inciting_incident": (
                "A districtwide deployment diverges across blocks at the same moment the archive's maintenance "
                "system exposes dangling objects, unsigned release refs, and incomplete mirrors."
            ),
            "central_problem": (
                "The district needs a provably correct history, trustworthy automation, scalable working practices, "
                "healthy object storage, and synchronized mirrors before critical services can reunify."
            ),
            "recurring_characters": [
                {
                    "name": "Director Imani Cross",
                    "role": "Head of reliability who frames each repository incident in operational terms.",
                },
                {
                    "name": "Jae Min",
                    "role": "A platform engineer responsible for worktrees, sparse checkouts, submodules, and automation.",
                },
                {
                    "name": "Rook",
                    "role": "A security analyst who challenges signatures, credentials, hooks, and protocol trust.",
                },
                {
                    "name": "Dr. Elian Voss",
                    "role": "An archive specialist who reveals Git's objects, refs, packs, and migration streams.",
                },
            ],
            "stakes": (
                "A mistaken forensic conclusion or unsafe maintenance action can make street services irreproducible, "
                "destroy recovery evidence, or allow an untrusted history to become authoritative."
            ),
            "chapter_progression": (
                "The learner masters revision language, searches hidden history, bisects failures, automates "
                "conflict reuse, scales working directories, configures behavior, verifies trust, restores and "
                "maintains object stores, serves repositories, migrates histories, and finally manipulates Git's "
                "object and ref machinery directly."
            ),
            "resolution": (
                "The districts converge on a verified history, mirrors are synchronized, automation is trusted, "
                "and the district archive can explain every ref down to its objects and transfer protocol."
            ),
            "learning_metaphor": {
                "revision_expression": "a query into the district's historical event graph",
                "worktree": "a separate operations floor attached to one archive",
                "hook": "an automated checkpoint in a deployment route",
                "object_database": "the immutable records beneath every visible street reference",
                "server_protocol": "the transport grid that exchanges objects and refs",
            },
        },
        "price": 700,
        "sort_order": 3,
        "is_published": True,
        "world_slug": "neon-backstreets",
        "difficulty": "advanced",
        "prerequisite_story": "frostbound-citadel",
    },
]
