"""Тестовая коллекция варианта 7: английские тексты по медицине и художественной критике."""

from __future__ import annotations

import os
import textwrap
from typing import Sequence

import pymupdf

CORPUS: Sequence[tuple[str, str, str, str]] = (
    (
        "01_med_clinical_trials.txt",
        "medicine",
        "Clinical Trials and Vaccine Safety",
        """
        A clinical trial is a controlled study that tests a vaccine, a drug, or a therapy in
        patients. Randomized clinical trials assign patients to a treatment group or a control
        group. A placebo may be used when no standard treatment exists. Double-blind methods
        hide the assignment from the physician and the patient.

        The primary endpoint of a vaccine trial is often prevention of infection. Secondary
        endpoints include side effects, fever, and other adverse events. Safety and efficacy
        must both be shown before public health agencies approve a vaccine.

        Antibodies are proteins of the immune system. After vaccination the body produces
        antibodies that recognize an antigen of the virus. This immune response can prevent
        severe disease even when mild infection still occurs. Population studies measure
        mortality and morbidity after a vaccination campaign.

        Clinical guidelines describe the dose and the schedule. A high dose may raise
        efficacy and also raise the risk of side effects. Chronic conditions such as diabetes
        or hypertension require separate analysis because they change the outcome.

        The article argues that transparent data from randomized trials remain the main
        scientific method for medical decisions about vaccines and new drugs.
        """,
    ),
    (
        "02_med_cardiovascular.txt",
        "medicine",
        "Cardiovascular Disease and Hypertension",
        """
        Cardiovascular disease includes conditions of the heart and the arteries. Hypertension
        is a chronic condition with high blood pressure. It raises the risk of stroke and of
        myocardial infarction. Atherosclerosis forms plaque in the vessels and narrows the
        arteries.

        Screening in primary care measures blood pressure and cholesterol. Lifestyle and
        drugs can treat hypertension. Beta blockers and other therapy reduce cardiac risk
        in many patients. Severe hypertension may require hospital care.

        Imaging of the heart and the vessels helps diagnosis. The physician uses the results
        together with symptoms such as pain and fever. An acute infarction is a surgical and
        medical emergency. Recovery depends on the time to treatment and on complications.

        Epidemiology studies a population and a cohort. Statistically significant results
        show that prevention is more effective than late treatment. Public health programs
        therefore describe diet, screening, and early therapy.

        The mechanism of disease includes inflammation of the vessel wall. Inflammatory
        cells and proteins take part in plaque growth. This pathway is a target for new
        drugs in modern medicine.
        """,
    ),
    (
        "03_med_inflammation.txt",
        "medicine",
        "Inflammation, Infection, and the Immune System",
        """
        Inflammation is a response of the immune system to infection, injury, or a pathogen.
        Acute inflammation produces pain, fever, and local heat. Chronic inflammation lasts
        longer and can damage tissue and organs. The immune system uses antibodies, cells,
        and receptors.

        Bacteria and viruses are common pathogens. Bacterial infection may need a drug that
        the hospital provides after diagnosis. Viral infection often requires supportive
        therapy because many viruses have no specific treatment. Vaccines prevent several
        infections by training immune memory.

        The nervous system, the lungs, the liver, and the kidney can all show inflammatory
        disease. A biopsy and imaging support the diagnosis when symptoms are not specific.
        Cancer may also create an inflammatory environment around a tumor.

        Clinical research describes pathways and mechanisms. A receptor on a cell can start
        a cascade of proteins. If this process remains active, chronic disease follows.
        New therapy tries to block the pathway without harming healthy tissue.

        Safety remains important. Adverse events during treatment must be reported. The
        physician and the nurse watch the patient for severe reactions after a dose. This
        article treats inflammation as a central process in modern medicine.
        """,
    ),
    (
        "04_art_impressionism.txt",
        "art",
        "Impressionist Painting and Broken Color",
        """
        Impressionism is a movement in painting that studies light and color in everyday
        landscape. The artist uses broken color and visible brushstrokes on the canvas.
        A plein air method places the painter in the landscape rather than in the studio.
        Critics of the first exhibition called the style unfinished.

        Formal analysis of an impressionist painting starts with palette, hue, and value.
        The composition often has a high horizon and a quiet middle ground. The foreground
        may show a figure or a boat, while the background dissolves into pale tones.
        Texture comes from impasto rather than from a smooth glaze.

        The viewer does not see a photographic landscape. The painting suggests a moment
        of looking. Light changes the local color of water and of leaves. This aesthetic
        claim is central to art criticism of impressionism.

        Museums now hang these canvases as masterpieces. The curatorial label describes
        the artist, the date, and the motif. Close looking still shows the risk the painter
        took: a bright, almost abstract surface that also remains a landscape.

        Art history reads impressionism as both a style and a social fact. The modern city,
        the new pigments, and the public exhibition changed how artists worked. Criticism
        should hold the visual analysis and the historical context together.
        """,
    ),
    (
        "05_art_sculpture_museum.txt",
        "art",
        "Sculpture in the Museum: Volume, Pedestal, and Display",
        """
        A sculpture occupies space in a way a painting does not. Volume, mass, and contour
        matter as much as surface. Bronze and marble remain classical materials. A statue
        on a pedestal organizes the gaze of the viewer in the museum room.

        Curatorial display can make a work monumental or intimate. The white cube gallery
        isolates the sculpture from everyday context. A label and a caption provide a
        short narrative, but the body of the viewer still completes the meaning by walking
        around the form.

        Art criticism of sculpture asks how light moves across the carved or cast surface.
        Shadows become part of the composition. A dramatic contrast may suggest power;
        a soft contour may suggest fragility. The critic should describe these facts before
        large symbolic claims.

        Collections in museums mix sacred and secular subjects. An altarpiece and a portrait
        belong to different genres, yet both can stand in the same exhibition. The curator
        argues through placement. That argument is itself a form of criticism.

        Contemporary installation challenges the pedestal. The work of art may occupy the
        whole room. Viewers enter the space rather than look at an object on the wall.
        This shift is a main subject of modern art history and of museum studies.
        """,
    ),
    (
        "06_art_portrait_chiaroscuro.txt",
        "art",
        "Portraiture, Gaze, and Chiaroscuro",
        """
        A portrait is a painting or a sculpture of a human figure that claims presence.
        The gaze of the sitter meets the viewer or turns away. Art criticism treats this
        choice as part of the meaning. A self-portrait adds another layer: the artist
        becomes the subject.

        Chiaroscuro is the contrast of light and shadow. Baroque painters used it for
        dramatic effect. A dark background isolates the face. Soft light on the skin
        produces volume without a sharp outline. The palette may be limited, yet the
        values are complex.

        Formal analysis notes the frame, the scale, and the gesture of the hands.
        Iconography may add a book, a brush, or a sacred symbol. These motifs do not
        replace looking. The critic still has to say how pigment sits on the canvas
        and how the composition holds the figure in space.

        Museums often hang portraits in a line along the wall. The exhibition then
        becomes a social narrative of patrons and artists. Beauty is not a sufficient
        verdict. Interpretation should include power, gender, and the studio commission
        without forgetting color and line.

        This article treats portraiture as a genre where visual art and historical
        evidence meet. Close looking remains the first method of art criticism, and
        chiaroscuro is one of its most powerful tools.
        """,
    ),
)


FONT_REGULAR = "/usr/share/fonts/TTF/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"


def _d(text: str) -> str:
    return textwrap.dedent(text).strip()


def write_pdf(path: str, title: str, body: str) -> None:
    regular = FONT_REGULAR if os.path.exists(FONT_REGULAR) else None
    bold = FONT_BOLD if os.path.exists(FONT_BOLD) else None
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    if regular:
        page.insert_font(fontname="body", fontfile=regular)
    if bold:
        page.insert_font(fontname="bold", fontfile=bold)
    body_font = "body" if regular else "helv"
    title_font = "bold" if bold else "hebo"
    y = 56
    for line in textwrap.wrap(title, width=70) or [title]:
        page.insert_text((50, y), line, fontsize=14, fontname=title_font)
        y += 20
    y += 12
    for paragraph in body.split("\n\n"):
        for line in textwrap.wrap(paragraph, width=90) or [""]:
            if y > 800:
                page = doc.new_page(width=595, height=842)
                if regular:
                    page.insert_font(fontname="body", fontfile=regular)
                if bold:
                    page.insert_font(fontname="bold", fontfile=bold)
                y = 56
            page.insert_text((50, y), line, fontsize=11, fontname=body_font)
            y += 15
        y += 8
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    doc.save(path)
    doc.close()


def ensure_corpus(documents_dir: str) -> list[dict]:
    os.makedirs(documents_dir, exist_ok=True)
    records = []
    for filename, domain, title, raw in CORPUS:
        body = _d(raw)
        txt_path = os.path.join(documents_dir, filename)
        pdf_path = os.path.splitext(txt_path)[0] + ".pdf"
        if not os.path.exists(txt_path):
            with open(txt_path, "w", encoding="utf-8") as file:
                file.write(title + "\n\n" + body + "\n")
        if not os.path.exists(pdf_path):
            write_pdf(pdf_path, title, body)
        records.append(
            {
                "filename": filename,
                "title": title,
                "domain": domain,
                "language": "english",
                "txt_path": txt_path,
                "pdf_path": pdf_path,
                "body": body,
            }
        )
    return records
