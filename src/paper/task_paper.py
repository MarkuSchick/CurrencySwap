import shutil

import pytask

from src.config import BLD
from src.config import ROOT
from src.config import SRC


document = "research_pres_30min"


@pytask.mark.latex(
    [
        "--pdf",
        "--interaction=nonstopmode",
        "--synctex=1",
        "--cd",
        "--quiet",
        "--shell-escape",
    ]
)
@pytask.mark.depends_on(
    [
        SRC / "paper" / f"{document}.tex",
        BLD / "figures" / "bootstrapped_eurlong_payout.png",
        BLD / "figures" / "bootstrapped_eurshort_payout.png",
        BLD / "figures" / "bootstrapped_negative_payout.png",
        BLD / "figures" / "bootstrapped_total_payout_EUR.png",
        BLD / "figures" / "bootstrapped_total_payout_USD.png",
        BLD / "figures" / "euro_usd_bootstrapped.png",
        BLD / "figures" / "euro_usd_historical.png",
        BLD / "figures" / "euro_usd_timeseries.png",
        BLD / "figures" / "historical_eurlong_payout.png",
        BLD / "figures" / "historical_eurshort_payout.png",
        BLD / "figures" / "historical_negative_payout.png",
        BLD / "figures" / "historical_total_payout_EUR.png",
        BLD / "figures" / "historical_total_payout_USD.png",
    ]
)
@pytask.mark.produces(BLD / "paper" / f"{document}.pdf")
def task_compile_documents():
    pass


@pytask.mark.depends_on(BLD / "paper" / f"{document}.pdf")
@pytask.mark.produces(ROOT / f"{document}.pdf")
def task_copy_to_root(depends_on, produces):
    shutil.copy(depends_on, produces)
