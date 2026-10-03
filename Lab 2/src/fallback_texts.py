"""Запасные тексты коллекции, если Wikipedia недоступна."""

from __future__ import annotations

import textwrap
from typing import Sequence


def _d(text: str) -> str:
    return textwrap.dedent(text).strip()


FALLBACK_CORPUS: Sequence[dict] = (
    {
        "filename": "01_en_cs_artificial_intelligence.pdf",
        "title": "Artificial Intelligence: Methods, Limits, and Scientific Practice",
        "reference": (
            "Artificial intelligence is the scientific study of computational systems that "
            "perform tasks associated with human cognition, including perception, reasoning, "
            "learning, and language. Modern research combines statistical learning with "
            "symbolic methods and evaluates models by generalization rather than by mimicry alone."
        ),
        "body": _d(
            """
            Artificial intelligence is the scientific study of computational systems that
            perform tasks associated with human cognition, including perception, reasoning,
            learning, and language. Modern research combines statistical learning with
            symbolic methods and evaluates models by generalization rather than by mimicry alone.
            The field is not a single algorithm. It is a family of representations, search
            procedures, and evaluation protocols that must be matched to a problem.

            Early programs encoded expert rules and searched discrete state spaces. Those
            systems could explain a decision, but they failed when the world departed from
            the knowledge base. The later statistical turn treated intelligence as estimation
            of functions from data. Supervised learning maps inputs to labels. Unsupervised
            learning discovers structure without labels. Reinforcement learning optimizes
            sequential decisions from reward. Each setting implies a different loss, a
            different notion of generalization, and a different failure mode.

            A neural network composes linear maps with nonlinear activations. Depth lets
            features be reused; width lets several hypotheses be represented in parallel.
            Convolution exploits locality in images. Recurrence and attention model sequences.
            Transformers replaced many recurrent designs because attention gives a differentiable
            routing mechanism over tokens. None of these architectures is magic. They amplify
            correlations present in the training distribution and remain silent about causes
            that never appear in that distribution.

            Representation learning is the practical core of contemporary computer science
            research on intelligence. Instead of hand-crafting features, a model is trained
            to construct features that make a downstream task linearly separable, or at least
            easier. Pretraining on large corpora followed by fine-tuning on a smaller labeled
            set is the dominant industrial recipe. The scientific question is not only whether
            accuracy rises, but which invariances the representation captured and which
            spurious shortcuts it exploited.

            Evaluation must separate interpolation from extrapolation. A test set drawn from
            the same mixture as the training set measures in-distribution performance. Robustness
            tests change lighting, dialect, hospital, or year. Calibration asks whether predicted
            probabilities match frequencies. Uncertainty matters in medicine and in control.
            A model that is confidently wrong is more dangerous than a model that abstains.

            Optimization theory explains why large networks can be trained at all. Stochastic
            gradient descent with momentum, adaptive step sizes, and normalization layers
            keep the trajectory in regions where gradients remain informative. Implicit bias
            of the optimizer often matters as much as the explicit loss. Two models with
            identical training error can differ violently on rare inputs because they selected
            different interpolating solutions.

            Symbolic methods have not disappeared. Constraint solvers, type systems, and
            knowledge graphs remain the correct tools when correctness is a specification,
            not a statistic. Hybrid research tries to keep the coverage of learning and the
            guarantees of search. Neuro-symbolic models use a network to propose candidates
            and a solver to filter them. The engineering difficulty is differentiable interfaces
            between discrete structure and continuous parameters.

            Language models illustrate both the promise and the confusion of the field. They
            compress distributional regularities of text and can be prompted to perform many
            tasks without task-specific architectures. They also hallucinate citations, leak
            training fragments, and inherit social bias. Treating a language model as a
            knowledge base is a category error: it is a sampler from a conditional distribution
            over tokens. Retrieval-augmented generation tries to ground answers in documents,
            which brings the problem back to information retrieval, ranking, and citation.

            Computer vision followed a similar arc from engineered descriptors to deep residual
            networks and then to vision transformers. The scientific contribution is not the
            named architecture, but the demonstration that hierarchical features can be learned
            end to end when data and compute are sufficient. Domain shift remains hard: a
            detector trained on sunny highways degrades in snow. Self-supervision on video
            and multimodal alignment with text are current attempts to buy more invariance
            without more labels.

            Ethics and safety are not decorations. Training data contain private records and
            copyrighted books. Deployment can automate discrimination at scale. Dual-use
            tools can assist both tutors and attackers. A responsible scientific article
            therefore reports data provenance, compute cost, and known failure cases with
            the same seriousness as it reports a new score on a benchmark.

            The research frontier is less about inventing yet another layer type and more
            about reliable abstraction. Causal models, mechanistic interpretability, energy
            efficient training, and evaluation under distribution shift are the questions
            that will decide whether artificial intelligence remains a collection of impressive
            demos or becomes a stable engineering discipline. Students of computer science
            should learn the mathematics of generalization, the systems that train large
            models, and the habit of asking what a metric does not measure.
            """
        ),
    },
    {
        "filename": "02_en_cs_operating_system.pdf",
        "title": "Operating Systems: Abstraction, Isolation, and Resource Control",
        "reference": (
            "An operating system is the privileged software that multiplexes hardware among "
            "programs, isolates faults, and offers stable abstractions such as processes, "
            "virtual memory, and files. Its quality is measured by correctness under concurrency, "
            "not by the beauty of a desktop shell."
        ),
        "body": _d(
            """
            An operating system is the privileged software that multiplexes hardware among
            programs, isolates faults, and offers stable abstractions such as processes,
            virtual memory, and files. Its quality is measured by correctness under concurrency,
            not by the beauty of a desktop shell. Without those abstractions each application
            would program devices, manage physical pages, and fight over the processor by hand.

            The process is the fundamental unit of execution and accounting. A process owns
            an address space, open descriptors, and credentials. Threads share that address
            space and complicate synchronization. The scheduler decides which thread runs.
            Fairness, latency, and throughput pull in different directions. A real-time subsystem
            may starve background batch work; an unfair scheduler can make a GUI feel broken
            even when the processor is mostly idle.

            Virtual memory decouples what a program thinks it has from what the machine
            physically provides. Page tables, translation lookaside buffers, and replacement
            policies implement this lie efficiently. Copy-on-write lets fork be cheap. Memory
            mapping turns file I/O into page faults. The cost of a fault, the size of a huge
            page, and NUMA placement now dominate performance of data intensive services.
            A scientific discussion of operating systems that ignores the memory hierarchy
            is incomplete.

            Isolation is a security property and a debugging property. Kernel mode, user mode,
            system calls, and capability or permission checks define the trusted computing
            base. A single unchecked copy_from_user is a historical source of catastrophe.
            Microkernels push services out of the privileged space; monolithic kernels keep
            them in for speed. Containers share a kernel and isolate namespaces; virtual
            machines add a hypervisor. The computer science question is which invariants
            remain after the optimization.

            File systems persist bytes with names, directories, and crash consistency.
            Journals, copy-on-write trees, and checksums exist because disks lie, power fails,
            and software bugs write the wrong block. POSIX semantics are a social contract
            more than a law of nature. Distributed file systems add network partitions and
            replica divergence. An operating system course that treats a file as an infinite
            reliable array prepares students badly for production.

            Concurrency control in the kernel uses locks, wait queues, RCU, and interrupt
            disabling. Deadlock is not a theoretical curiosity; it is an outage. Lock ordering
            protocols, lockdep, and formal models of concurrency are tools of the trade.
            Device drivers remain the largest source of kernel defects because they combine
            asynchrony, hardware errata, and vendor pressure. Language based isolation and
            verified drivers are active research, not museum pieces.

            Networking stacks turn packets into sockets. Protocol processing can live in the
            kernel, in user space with kernel bypass, or in programmable hardware. Latency
            budgets of microseconds force batching, zero copy, and careful cache behavior.
            An operating system that copies every byte twice will lose to one that does not,
            regardless of the elegance of its process model.

            Persistence of control policies matters as much as persistence of files. Access
            control lists, mandatory access control, seccomp filters, and attestation try to
            make least privilege enforceable. The human interface to these mechanisms is often
            the weakest layer. A perfect reference monitor with an unreadable policy language
            will be disabled by an operator. Systems research therefore includes measurement
            of administrator error, not only of cycles.

            Teaching operating systems still proceeds through the classical path: boot, traps,
            processes, memory, files, and a small kernel written by students. That path remains
            correct. What changed is the scale. A warehouse computer is an operating system
            problem distributed across racks. Scheduling then includes placement, energy,
            and failure domains. The abstractions survive; the implementations become empirical
            and noisy.

            The scientific article on operating systems should therefore keep two stories
            together. One story is mathematical: safety properties of isolation, liveness of
            schedulers, consistency of storage. The other is experimental: traces, tail latencies,
            and the surprising cost of a cache miss. Computer science advances when those
            stories constrain each other rather than live in separate conferences.
            """
        ),
    },
    {
        "filename": "03_en_lit_hamlet.pdf",
        "title": "Delay, Theatre, and Conscience in Shakespeare’s Hamlet",
        "reference": (
            "Hamlet is a tragedy of thought performed as action that never quite arrives. "
            "Shakespeare stages a prince who can name every moral complication of revenge "
            "and who therefore becomes the delay he describes. The play is not a riddle about "
            "a missing will to act; it is a study of how conscience, theatre, and inheritance "
            "share one vocabulary."
        ),
        "body": _d(
            """
            Hamlet is a tragedy of thought performed as action that never quite arrives.
            Shakespeare stages a prince who can name every moral complication of revenge
            and who therefore becomes the delay he describes. The play is not a riddle about
            a missing will to act; it is a study of how conscience, theatre, and inheritance
            share one vocabulary. Elsinore is a court that listens, spies, and repeats, so
            every private sentence is already public.

            The ghost demands a son's duty in the language of a murdered king. Hamlet receives
            that demand as both law and contamination. To kill Claudius would restore a lineage
            and would also copy the crime that destroyed it. The prince's questions about the
            ghost's nature are not pedantry. If the spirit is a devil, revenge is damnation.
            If the spirit tells the truth, delay is betrayal. Shakespeare refuses to let the
            audience hold a simpler theology than the protagonist.

            Theatre inside the play is Hamlet's laboratory. The Mousetrap is an experiment
            about evidence: Claudius's face will confess if the fiction is well enough aimed.
            The experiment works and solves nothing, because proof of guilt is not yet a
            politics of succession. Hamlet learns that art can catch a conscience and that
            catching a conscience does not clean a state. The players also give him a mirror
            for his own rhetoric. He scolds them for overacting while he himself performs
            madness for an audience of courtiers.

            Madness is a costume and a leak. Ophelia is destroyed by the same court language
            that Hamlet can still manipulate. Her songs say plainly what his soliloquies
            decorate. Gertrude's desire, Polonius's surveillance, and Laertes's imported
            revenge plot are not subplots; they are the social machine that makes Hamlet's
            interiority expensive. A literature essay that treats the prince as a modern
            patient in isolation misses the play's cruelty: thought is never private in a
            surveillance court.

            Time in Hamlet is rotten because mourning is interrupted. The marriage follows
            the funeral too quickly, and the prince is asked to change clothes before grief
            has finished its work. Delay then becomes a fidelity to duration. When Hamlet
            finally kills, the stage is already crowded with other deaths that his delay did
            not prevent. Fortinbras inherits a kingdom emptied by intelligence that could
            not become policy. The ending is not a reward for action; it is an inventory
            of what thinking cost.

            Language does the killing as surely as rapiers. Puns, reports, and letters
            circulate poison. The play is obsessed with copies: a ghost that looks like a
            king, a nephew who plays a fool, a play that copies a murder, a fencing match
            that copies honest sport. Romantic readers sometimes want a single authentic
            Hamlet behind the roles. The text offers instead a man who exists as quotation,
            soliloquy, and rumor. That is why the part remains inexhaustible for actors.
            Each production chooses which copy to trust.

            A responsible reading keeps the political plot visible. Denmark is an elective
            monarchy under threat, and Claudius is a competent administrator as well as a
            murderer. Hamlet's disgust at the world includes misogyny that the play neither
            fully endorses nor clearly punishes. Literature is not improved by washing the
            prince into an emblem of pure intellect. He is witty, cruel, tender, and late.
            The essay that can hold those tones together is closer to Shakespeare than the
            essay that solves him.
            """
        ),
    },
    {
        "filename": "04_en_lit_romanticism.pdf",
        "title": "Romanticism: Imagination, Nature, and the Unfinished Self",
        "reference": (
            "Romanticism names a set of European aesthetic revolts around 1800 that trusted "
            "imagination against mechanical explanation. It is not a single style. It is a "
            "claim that inner life, landscape, and history are continuous, and that poetry "
            "can witness that continuity without reducing it to a moral."
        ),
        "body": _d(
            """
            Romanticism names a set of European aesthetic revolts around 1800 that trusted
            imagination against mechanical explanation. It is not a single style. It is a
            claim that inner life, landscape, and history are continuous, and that poetry
            can witness that continuity without reducing it to a moral. The movement arrives
            after revolution and industrial acceleration, so its pastorals are never innocent.
            Even a lake poem knows about cities.

            Wordsworth and Coleridge made memory a philosophical instrument. The spot of
            time is not nostalgia; it is an epistemology. Recollection reorganizes sensation
            until a landscape becomes a teacher. Keats later distrusts that confidence and
            prefers a negative capability that remains with uncertainty. Shelley treats the
            poet as an unacknowledged legislator, which is both arrogance and a theory of
            political form. These disagreements are the movement. A textbook that flattens
            them into love of nature has already left literature for tourism.

            German Romanticism adds fragment, irony, and the infinite. Novalis and the
            Schlegel circle treat the unfinished work as the only honest one, because the
            absolute cannot be exhibited as a closed system. French Romanticism, from Rousseau's
            sensibility to Hugo's theatre, makes the people and the grotesque enter the
            sacred space of tragedy. English, German, and French strains should not be
            merged into one perfume. Comparative reading is the point of a literature essay.

            Nature in Romantic writing is never merely scenery. Storms, ruins, and mountains
            exteriorize a mind that no longer believes the social order is natural. The sublime
            is an education in scale: the self discovers its smallness and, paradoxically,
            its intensity. Later ecological criticism can use this archive, but it should not
            pretend that Wordsworth invented carbon ethics. He invented a way of attending.
            Attention is already a politics when enclosure and factories rewrite the land.

            The Romantic self is theatrical. Byron sells a mask so successfully that the mask
            becomes a European export. Confessional intensity in De Quincey or in later
            autobiographies shows the cost of that export: opium, debt, and a public that
            wants more interiority than a person can survive. Feminist rereading restores
            Dorothy Wordsworth, Mary Shelley, and the women who wrote gothic novels as
            theorists, not as muses. Frankenstein is a Romantic essay about making, education,
            and abandoned responsibility, not a Halloween accessory.

            Form matters. The lyric ode, the conversation poem, the historical novel, and
            the fragment are experiments in time. They try to hold duration on a page that
            the reader finishes too quickly. Music and painting of the period pursue the same
            problem with different materials. A literature student who only extracts themes
            will miss why an ode turns, why a stanza breaks, why a novel withholds a confession.
            Romanticism is a workshop of forms for feelings that Enlightenment prose found
            improper.

            The afterlife of Romanticism is modernity's unfinished argument with it. Realism
            mocks its excess, modernism inherits its fragment, and popular culture still
            sells Byronic heroes. To write an essay on Romanticism today is to decide which
            inheritance to keep: the discipline of attention, the suspicion of systems, or
            the glamour of the isolated genius. The first two remain usable. The third was
            always a marketing campaign that the best Romantic poems already doubted.
            """
        ),
    },
    {
        "filename": "05_fr_cs_intelligence_artificielle.pdf",
        "title": "L'intelligence artificielle comme science de la généralisation",
        "reference": (
            "L'intelligence artificielle étudie des systèmes informatiques capables d'accomplir "
            "des tâches associées à la cognition: percevoir, classer, traduire, décider. "
            "La question scientifique n'est pas l'imitation de l'humain, c'est la généralisation "
            "hors des exemples d'apprentissage."
        ),
        "body": _d(
            """
            L'intelligence artificielle étudie des systèmes informatiques capables d'accomplir
            des tâches associées à la cognition: percevoir, classer, traduire, décider.
            La question scientifique n'est pas l'imitation de l'humain, c'est la généralisation
            hors des exemples d'apprentissage. Un modèle qui réussit uniquement sur le jeu
            d'entraînement n'est pas intelligent; il est une table de correspondances coûteuse.

            L'histoire du domaine alterne entre systèmes symboliques et approches statistiques.
            Les systèmes experts expliquaient leurs décisions mais cassaient dès que le monde
            sortait de la base de règles. L'apprentissage automatique a inversé le programme:
            on estime une fonction à partir de données. Apprentissage supervisé, non supervisé
            et par renforcement ne sont pas des modes d'un logiciel, ce sont des hypothèses
            différentes sur ce qui constitue un signal.

            Un réseau de neurones compose des transformations linéaires et des non-linéarités.
            La convolution exploite la localité des images. L'attention des transformeurs
            permet de router l'information entre jetons d'une séquence. Ces architectures
            n'inventent pas du sens; elles compressent des corrélations. Si une corrélation
            est spurie, le système la reproduira avec assurance. D'où l'importance des
            décalages de distribution, de la calibration et des protocoles d'évaluation
            qui ne se réduisent pas à un score unique.

            L'apprentissage de représentations est le cœur pratique de la recherche actuelle.
            On pré-entraîne sur un large corpus, puis on adapte le modèle à une tâche étiquetée
            plus petite. La science consiste à comprendre quelles invariances ont été acquises.
            Un descripteur robuste à la lumière et fragile à l'hôpital d'origine n'a pas appris
            la maladie; il a appris un artefact. Les articles sérieux rapportent ces échecs
            avec la même précision que les records.

            Les méthodes symboliques restent indispensables lorsque la correction est une
            spécification: types, solveurs, bases de connaissances. Les approches hybrides
            cherchent à garder la couverture de l'apprentissage et les garanties de la recherche.
            L'interface entre structures discrètes et paramètres continus est le vrai problème
            d'ingénierie. Sans cette interface, on obtient soit un moteur statistique opaque,
            soit un système logique trop pauvre.

            Les modèles de langue illustrent la confusion publique du domaine. Ils échantillonnent
            une distribution conditionnelle sur des jetons. Les traiter comme une encyclopédie
            est une erreur de catégorie. L'augmentation par recherche documentaire ramène
            alors le problème à celui des systèmes d'information: indexer, classer, citer.
            L'informatique de l'intelligence artificielle rejoint ici l'informatique de la
            recherche d'information.

            L'évaluation doit distinguer interpolation et extrapolation. Un jeu de test tiré
            de la même mixture que l'entraînement mesure une performance intra-distribution.
            Les tests de robustesse changent l'année, l'accent, l'appareil photo. L'incertitude
            compte en médecine et en commande. Un système très confiant et faux est plus
            dangereux qu'un système qui s'abstient. La recherche contemporaine sur la
            quantification d'incertitude n'est donc pas un luxe.

            L'éthique n'est pas un chapitre collé à la fin. Les corpus contiennent des données
            personnelles et des œuvres protégées. Le déploiement peut automatiser une
            discrimination. Un article scientifique responsable décrit la provenance des
            données, le coût de calcul et les cas d'échec connus. Les étudiants en informatique
            doivent apprendre la théorie de la généralisation, les systèmes qui entraînent
            les grands modèles, et l'habitude de demander ce qu'une métrique ne mesure pas.
            """
        ),
    },
    {
        "filename": "06_fr_cs_base_de_donnees.pdf",
        "title": "Bases de données: modèles, transactions et intégrité",
        "reference": (
            "Une base de données est un système qui mémorise des faits partagés avec des "
            "garanties d'intégrité, d'isolation et de reprise après panne. Le modèle relationnel "
            "reste l'abstraction centrale, même lorsque le stockage physique est distribué "
            "ou documentaire."
        ),
        "body": _d(
            """
            Une base de données est un système qui mémorise des faits partagés avec des
            garanties d'intégrité, d'isolation et de reprise après panne. Le modèle relationnel
            reste l'abstraction centrale, même lorsque le stockage physique est distribué
            ou documentaire. Sans cette abstraction, chaque application réinvente des fichiers,
            des verrous et des copies de secours, et perd.

            Codd a séparé le schéma logique de l'implémentation. Relations, clés, contraintes
            et algèbre offrent un langage pour poser des questions sans décrire un parcours
            de pages. SQL est une incarnation imparfaite mais universelle de cette idée.
            L'optimisation de requêtes transforme une intention déclarative en plan physique:
            choix des index, ordre des jointures, poussée des sélections. Un cours d'informatique
            qui enseigne SQL comme une syntaxe et non comme un plan d'exécution forme des
            utilisateurs, pas des concepteurs.

            Les transactions donnent un sens au temps concurrent. Atomicité, cohérence,
            isolation et durabilité ne sont pas un slogan marketing; ce sont des invariants.
            Les niveaux d'isolation existent parce que la sérialisabilité stricte est chère.
            Un anomalie de lecture n'est pas un détail: elle devient un bug métier. Le
            contrôle de concurrence par verrous ou par versions a des coûts mesurables sur
            les queues de latence. Les systèmes modernes rendent ces coûts visibles.

            L'intégrité référentielle et les contraintes d'unicité protègent le sens des
            données contre les applications pressées. Quand on relâche ces contraintes pour
            aller plus vite, on achète un débit et on vend des anomalies. Les entrepôts
            analytiques acceptent souvent cette transaction: ils copient, dénormalisent,
            et recalculent. Les bases opérationnelles ne peuvent pas toujours se le permettre.
            Distinguer OLTP et OLAP n'est pas une mode, c'est une physique des accès.

            La distribution casse l'illusion d'un disque unique. Réplication, partitionnement
            et consensus deviennent alors le système d'exploitation des données. Le théorème
            CAP est trop souvent cité comme une excuse. En pratique on choisit des fenêtres
            de cohérence, des quorum, des files de rattrapage. Un article scientifique sur
            les bases doit montrer ces protocoles, pas seulement un schéma entité-association.

            Les modèles non relationnels ont une utilité réelle: documents, graphes, séries
            temporelles. Leur erreur pédagogique est de laisser croire que l'absence de schéma
            abolit le schéma. Le schéma migre dans le code. Quand dix services écrivent des
            champs différents sous le même nom, on a recréé une base mauvaise. La science
            des données persistantes consiste à rendre les invariants explicites, quel que
            soit le format du fichier.

            L'administration est une partie de la science. Sauvegardes, journaux, statistiques
            d'optimiseur, plans de capacité déterminent si le modèle survit au lundi matin.
            Un index mal choisi peut être pire que l'absence d'index. Le coût d'une contrainte
            se paie à l'écriture et se gagne à la lecture. Ces arbitrages se mesurent.
            L'informatique des bases de données est expérimentale autant qu'algébrique.

            Pour un système d'information, la base n'est pas un tiroir. C'est le contrat
            entre des métiers qui ne se font pas confiance. Modéliser, c'est décider quelles
            contradictions le monde a le droit d'avoir. Les étudiants doivent donc apprendre
            ensemble le calcul relationnel, le fonctionnement d'un moteur, et la lecture
            d'un plan d'exécution réel. Sans ces trois langues, on ne conçoit pas un système,
            on empile des tables.
            """
        ),
    },
    {
        "filename": "07_fr_lit_les_miserables.pdf",
        "title": "Les Misérables: justice, conversion et roman-monde",
        "reference": (
            "Les Misérables de Victor Hugo est un roman de la conversion qui refuse de séparer "
            "l'âme et la ville. Jean Valjean n'est pas seulement un ancien forçat devenu juste; "
            "il est le lieu où la loi, la charité et l'histoire nationale se disputent un "
            "même corps."
        ),
        "body": _d(
            """
            Les Misérables de Victor Hugo est un roman de la conversion qui refuse de séparer
            l'âme et la ville. Jean Valjean n'est pas seulement un ancien forçat devenu juste;
            il est le lieu où la loi, la charité et l'histoire nationale se disputent un
            même corps. Le livre procède par digressions parce que le malheur social ne tient
            pas dans une intrigue linéaire. Waterloo, les égouts, le couvent, l'argot: autant
            d'encyclopédies nécessaires à la morale.

            Javert incarne la loi comme géométrie. Il ne hait pas Valjean; il ne peut pas
            concevoir un homme plus grand que le code. Son suicide n'est pas un mélodrame
            superflu. C'est l'effondrement d'une épistémologie: si le criminel peut être
            vertueux, le monde de Javert n'a plus de coordonnées. Hugo ne se contente pas
            d'opposer le cœur à la police. Il montre que la police est une métaphysique.

            Fantine et Cosette déplacent le roman vers l'économie sexuelle du XIXe siècle.
            La misère n'est pas un décor; elle est une machine qui produit l'abandon.
            Thénardier transforme l'hospitalité en prédation, ce qui est une parodie amère
            de la société de commerce. Un essai littéraire qui ne lit que l'idylle de Marius
            et Cosette rate le prix que le roman fait payer aux femmes pour que la rédemption
            masculine reste visible.

            Les barricades de 1832 inscrivent le roman dans une mémoire républicaine encore
            chaude. Gavroche n'est pas un mascotte; il est l'enfant de Paris comme théorie
            politique: la rue éduque plus vite que l'école quand l'État abandonne. Hugo
            écrit après 1848 et 1851, et le récit porte cette après-coup. L'échec de la
            barricade n'annule pas la justice de la demande. Le roman tient ensemble deuil
            et exhortation, ce qui agace parfois le goût réaliste et constitue pourtant sa
            force oratoire.

            Le style hugolien accumule, énumère, éclaire. On peut le trouver excessif.
            L'excès est ici une éthique: trop de pauvres restent hors cadre si la phrase
            reste sobre. Le romancier se fait prêtre, historien, urbaniste. Cette hybridation
            des genres est le vrai dispositif formel des Misérables. Ce n'est pas un roman
            qui contient des essais; c'est un essai qui a besoin de personnages pour ne pas
            mentir.

            La lumière et l'ombre organisent la morale visuelle du livre. Le chandelier de
            Monseigneur Myriel, la teinturerie, le tout-à-l'égout, la lumière de Cosette:
            objets et lieux baptisent les âmes. Lire Hugo, c'est accepter que le symbole
            ne soit pas une faiblesse. Dans une tradition réaliste plus tardive, le symbole
            sera suspect. Chez Hugo, il est une méthode pour rendre visible l'invisible social.

            Un essai contemporain doit aussi noter ce que le roman exclut ou idéalise. Le
            peuple est souvent chanté plus qu'entendu dans sa contradiction interne. La
            rédemption par le sacrifice peut sanctifier la souffrance au lieu de la combattre.
            Ces objections n'annulent pas l'œuvre; elles la gardent dans l'histoire. Les
            Misérables restent un laboratoire où la littérature française teste si l'épopée
            démocratique est encore possible après la Terreur et avant la Commune.
            """
        ),
    },
    {
        "filename": "08_fr_lit_letranger.pdf",
        "title": "L'Étranger de Camus: indifférence, soleil et tribunal du langage",
        "reference": (
            "L'Étranger d'Albert Camus raconte un meurtre au passé composé et un procès au "
            "présent moral. Meursault n'est pas un monstre opaque; il est un homme qui refuse "
            "les phrases toutes faites du deuil, de l'amour et de la faute, jusqu'à ce que "
            "la société les prononce à sa place."
        ),
        "body": _d(
            """
            L'Étranger d'Albert Camus raconte un meurtre au passé composé et un procès au
            présent moral. Meursault n'est pas un monstre opaque; il est un homme qui refuse
            les phrases toutes faites du deuil, de l'amour et de la faute, jusqu'à ce que
            la société les prononce à sa place. Le premier livre décrit des sensations. Le
            second décrit des interprétations. Le roman est cette bascule.

            La mort de la mère ouvre le texte par une indifférence qui scandalise plus tard
            les jurés plus que le coup de feu. Camus montre que la société colonial française
            d'Alger tolère la violence mieux qu'elle ne tolère l'absence de rhétorique
            funèbre. Meursault fume, boit un café au lait, va nager. Ces gestes sont lus
            comme des preuves. Le roman enseigne ainsi la littérature comme mauvais tribunal:
            on y condamne un style de présence au monde.

            Le soleil n'est pas un décor méditerranéen de carte postale. C'est une force
            physique qui saturent les perceptions jusqu'à la rupture. Sur la plage, la lumière
            et le sel précèdent l'intention. On a trop dit que Meursault tuait sans raison.
            Le texte donne des raisons sensorielles et refuse les raisons morales attendues.
            Cette différence est le nœud de l'absurde camusien: le monde est trop présent,
            les justifications trop tardives.

            Marie, Raymond, le robot de bureau, le voisin au chien: une sociabilité pauvre
            et exacte. Camus n'écrit pas un traité, il écrit des scènes où l'amitié est une
            habitude plus qu'un serment. Le colonialisme apparaît dans la rixe, l'Arabe sans
            prénom, la plage comme frontière. Un essai contemporain ne peut plus lire L'Étranger
            comme une fable universelle sans terre. L'universel camusien passe par une Algérie
            réelle, inégale, chauffée à blanc.

            Le procès invertit le fardeau de la preuve. On ne demande plus seulement si
            Meursault a tiré; on demande s'il a pleuré. L'avocat, le procureur et l'aumônier
            parlent une langue que le narrateur n'habite pas. D'où la sécheresse du style:
            phrases courtes, parataxe, passé composé. La forme refuse la causalité psychologique
            que le tribunal exige. Lire Camus, c'est donc lire une grammaire politique.

            La fin n'offre pas une conversion chrétienne, malgré la tentation de l'aumônier.
            Meursault s'ouvre à la tendresse indifférente du monde et à l'idée que les
            spectateurs de son exécution pourraient le haïr. C'est une communion inversée.
            L'absurde n'y est pas un slogan de lycée; c'est une éthique de la lucidité sans
            consolation. On peut discuter si cette éthique suffit devant l'histoire. On ne
            peut pas dire que le roman soit simple.

            La postérité scolaire a parfois réduit L'Étranger à l'indifférence d'un antihéros.
            Mieux vaut y voir un conflit de langages. D'un côté, le corps, la mer, le sommeil.
            De l'autre, le dossier, le Dieu, la mère idéale. La littérature, ici, n'orne pas
            le droit: elle montre comment le droit se nourrit de récits. Un essai réussi
            tient ensemble la phrase camusienne, le soleil comme agent, et le tribunal comme
            machine à fiction.
            """
        ),
    },
)
