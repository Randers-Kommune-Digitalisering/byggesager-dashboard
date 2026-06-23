import streamlit as st

from utils.logo import get_logo
from page.sagsbehandlingstid import get_sagsbehandlingstid_overview
from page.byggesager import get_byggesager_overview
from page.landzone import get_landzonesager_overview


st.set_page_config(
    page_title="Byggesager",
    page_icon="assets/favicon.ico",
)


PAGES = {
    "sagsbehandlingstid": {
        "label": "Sagsbehandlingstid",
        "function": get_sagsbehandlingstid_overview,
    },
    "byggesager": {
        "label": "Byggesager",
        "function": get_byggesager_overview,
    },
    "landzonesager": {
        "label": "Landzonesager",
        "function": get_landzonesager_overview,
    },
}


st.markdown(
    """
<style>
/* Entire sidebar */
[data-testid="stSidebar"] {
    background-color: #f0f0f0;
}

/* Sidebar content spacing */
[data-testid="stSidebarContent"] {
    padding-top: 1rem;
}

/* Byggesager heading */
.byggesager-heading {
    display: flex;
    align-items: center;
    gap: 14px;

    margin: 24px 12px 20px 12px;
    color: #4a4a4a;
}

/* Heading icon */
.byggesager-heading-icon {
    width: 27px;
    height: 27px;
    flex-shrink: 0;
}

/* Heading text */
.byggesager-heading-text {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.35;
}

/* Divider underneath heading */
.byggesager-divider {
    border: none;
    border-top: 1px solid #bcbcbc;
    margin: 0 12px 14px 12px;
}

/* Menu container */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 5px;
}

/* Each menu item */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label {
    display: flex;
    align-items: flex-start;

    width: 100%;
    min-height: 54px;

    padding: 13px 16px;
    margin: 0;

    border-radius: 9px;
    cursor: pointer;
}

/* Hover effect */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:hover {
    background-color: #e0e0e0;
}

/* Selected menu item */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:has(input:checked) {
    background-color: #d0d0d0;
}

/* Hide the normal radio circle */
[data-testid="stSidebar"]
div[role="radiogroup"]
input {
    display: none;
}

/* Hide Streamlit's radio-control wrapper */
[data-testid="stSidebar"]
div[role="radiogroup"]
label > div:first-child {
    display: none;
}

/* Menu text */
[data-testid="stSidebar"]
div[role="radiogroup"]
label p {
    margin: 0;

    color: #303030;
    font-size: 17px;
    line-height: 1.45;

    white-space: normal;
    overflow-wrap: break-word;
}

/* Selected menu text */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:has(input:checked)
p {
    color: #4a4a4a;
    font-weight: 700;
}

/* Shared icon area */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label::before {
    content: "";

    display: block;
    width: 21px;
    height: 21px;
    flex: 0 0 21px;

    margin-top: 2px;
    margin-right: 12px;

    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
}

/* Sagsbehandlingstid icon */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:nth-of-type(1)::before {
    background-image: url(
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/building-fill-gear.svg"
    );
}

/* Byggesager icon */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:nth-of-type(2)::before {
    background-image: url(
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/building.svg"
    );
}

/* Landzonesager icon */
[data-testid="stSidebar"]
div[role="radiogroup"]
> label:nth-of-type(3)::before {
    background-image: url(
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/geo-alt-fill.svg"
    );
}
</style>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    # Existing Randers Kommune logo.
    st.markdown(
        get_logo(),
        unsafe_allow_html=True,
    )

    # Handmade heading.
    st.markdown(
        """
<div class="byggesager-heading">
    <img
        class="byggesager-heading-icon"
        src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/building.svg"
        alt=""
    >
    <div class="byggesager-heading-text">
        Byggesager
    </div>
</div>
<hr class="byggesager-divider">
""",
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        options=list(PAGES.keys()),
        format_func=lambda page: PAGES[page]["label"],
        label_visibility="collapsed",
        key="byggesager_sidebar_navigation",
    )


# Open the selected page.
PAGES[selected_page]["function"]()