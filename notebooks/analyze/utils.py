import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from adjustText import adjust_text
import seaborn as sns

# Misc. functions
def tee(df, fn, *args, **kwargs):
    fn(df, *args, **kwargs)
    return df

def save(df, dest, *args, **kwargs):
    default_kwargs = dict(index = False)
    default_kwargs.update(kwargs)
    df.to_csv(dest, *args, **default_kwargs)
    return df

# Charting functions

def percentify_axes(ax, lim = (0, 1), name = "y"):
    axis = getattr(ax, name + "axis")
    axis.set_ticks(pd.np.arange(0, 1.1, 0.1))
    axis.set_ticklabels([ "{:.0f}%".format(y * 100)
        for y in getattr(ax, "get_{}ticks".format(name))() ])
    
    getattr(ax, "set_{}lim".format(name))(*lim)
    return ax

def plot_rates(rates, title = None, **kwargs):
    plot_kwargs = dict(
        ylim = (0, 1),
        figsize = (10, 6),
        lw = 2,
        grid = True,
        title = title,
        legend = True,
    )
    plot_kwargs.update(kwargs)
    ax = rates.plot(
        **plot_kwargs
    )
    percentify_axes(ax)
    if plot_kwargs["legend"]:
        leg = ax.get_legend()
        plt.setp(leg.get_texts() + [leg.get_title()], fontsize = 12)
    return ax

def make_histogram_grid(df, col, row, hue, value, title = None, **kwargs):
    PCTS_BY_FIVE = pd.np.arange(0, 1.05, 0.05)

    fg_kwargs = dict(
        margin_titles = True,
        sharey = True,
        sharex = False,
        height = 2.5,
        aspect = 2,
        palette = "PuBu"
    )
    
    fg_kwargs.update(kwargs)
    
    def hist(series, *args, **kwargs):
        if series.max() <= 1 and series.min() >= 0:
            bins = PCTS_BY_FIVE
        else:
            bins = pd.np.arange(-1, 1.05, 0.05)
            
        return plt.hist(
            series,
            density = True,
            bins = bins,
            edgecolor = "white",
            *args,
            **kwargs,
        )
    
    g = (
        sns.FacetGrid(
            df,
            row = row,
            hue = hue,
            col = col,
            **fg_kwargs
        )
        .map(hist, value)
        .map(
            lambda x, **kwargs: plt.axvline(
                x.median(),
                **kwargs
            ),
            value,
            color = "red"
        )
    )
    
    g.fig.subplots_adjust(wspace=0.2, hspace=0.75)
    
    for ax in g.axes.flatten():
        ax.set_xticklabels([ "{:.0f}%".format(x * 100) for x in ax.get_xticks() ])
        ax.set_yticklabels([ "{:.0f}%".format(100 * y * 0.05) for y in range(4) ])
        ax.set_ylabel("Pct. of Agencies")

    g.fig.suptitle(title)

    g.fig.subplots_adjust(top = 0.80)
    g.fig.set_facecolor("white")

    return g

# Data loading

## Return A
def load_reta_metadata():
    return (
        pd.read_csv(
        "../../data/standardized/reta-agency-metadata.csv",
        )
        .assign(
            larger_city = lambda x: x["ori_group"].isin([
                "1A",
                "1B",
                "1C",
                "2"
            ])
        )
        .loc[lambda df: df["year"] >= 1965]
    )

def load_reta_metadata_2016():
    agency_metadata = load_reta_metadata()

    return (
        agency_metadata

        .loc[lambda df: df["year"] <= 2016]
        
        .sort_values("year", ascending = False)
        
        .drop_duplicates(subset = [ "agency_ori_7" ])
    )

def reta_edit_number(df, ori, year, offense, col, adjustment):
    copy = df.copy()
    selector = lambda df: (
        (df["agency_ori_7"] == ori) &
        (df["year"] == year) &
        (df["offense"] == offense)
    )
    assert len(copy.loc[selector]) == 1
    prev_value = copy.loc[selector, col].iloc[0]
    copy.loc[selector, col] = (prev_value + adjustment)
    return copy

RETA_MASS_MURDER_ADJUSTMENTS = [
    # Oklahoma City bombing
    ("OK05506", 1995, "murder", "actual", -168),
    ("OK05506", 1995, "murder", "cleared", -168),

    # Pulse shooting; clearances not reflected in clearance count
    ("FL04804", 2016, "murder", "actual", -49),

    # Las Vegas shooting
    ("NV00201", 2017, "murder", "actual", -58),
    ("NV00201", 2017, "murder", "cleared", -58),

    # NOTE: None of these agencies submit data to NIBRS.
]

def reta_remove_mass_murder_events(counts):
    adjusted = counts.copy()
    for adj in RETA_MASS_MURDER_ADJUSTMENTS:
        adjusted = reta_edit_number(adjusted, *adj)
    return adjusted

def load_reta_annual_counts():
    agency_metadata = load_reta_metadata()
    agency_metadata_2016 = load_reta_metadata_2016()

    annual_counts = pd.read_csv(
        "../../data/standardized/reta-annual-counts.csv",
        low_memory = False
    )

    nongun_assaults = (
        annual_counts
        .loc[lambda df: df["offense"].isin([
            "assault_hands",
            "assault_knife",
            "assault_othweap" 
        ])]
        .groupby([
            "agency_ori_7",
            "year"
        ])
        [[
            "actual",
            "cleared"
        ]]
        .sum()
        .assign(offense = "assault_nongun")
        .reset_index()
        [list(annual_counts.columns)]
    )

    all_agg_assaults = (
        annual_counts
        .loc[lambda df: df["offense"].isin([
            "assault_gun",
            "assault_hands",
            "assault_knife",
            "assault_othweap" 
        ])]
        .groupby([
            "agency_ori_7",
            "year"
        ])
        [[
            "actual",
            "cleared"
        ]]
        .sum()
        .assign(offense = "assault_all")
        .reset_index()
        [list(annual_counts.columns)]
    )

    main_metadata_cols = [
        "year",
        "agency_ori_7",
        "ori_group",
        "larger_city",
    ]

    return (
        pd.concat([
            (
                annual_counts
                .loc[lambda df: df["offense"].isin([
                    "murder",
                    "assault_gun",
                ])]
            ),
            nongun_assaults,
            all_agg_assaults
        ])

        .pipe(reta_remove_mass_murder_events)
        
        .merge(
            agency_metadata[main_metadata_cols],
            how = "left",
            on = [ "agency_ori_7", "year" ]
        )
        
        .merge(
            agency_metadata_2016
            [main_metadata_cols]
            .drop(columns = [ "year" ]),
            how = "left",
            on = [ "agency_ori_7" ],
            suffixes = [ "_report", "_2016" ]
        )
        
        .loc[lambda df: df["year"] >= 1965]
    )



## Supplementary Homicide Reports
def load_shr_metadata():
    return (
        pd.read_csv(
        "../../data/standardized/shr-agency-metadata.csv",
        )
        .assign(
            larger_city = lambda x: x["ori_group"].isin([
                "1A",
                "1B",
                "1C",
                "2"
            ])
        )
    )

def load_shr_metadata_2016():
    agency_metadata = load_shr_metadata()

    return (
        agency_metadata

        .loc[lambda df: df["year"] <= 2016]
        
        .sort_values("year", ascending = False)
        
        .drop_duplicates(subset = [ "agency_ori_7" ])
    )

def shr_remove_mass_murder_events(victims):
    incidents_to_exclude = [
        # 1995 Oklahoma City bombing
        "OK05506|95|04|006",
        "OK05506|95|04|007",
        "OK05506|95|04|008",
        "OK05506|95|04|009",
        "OK05506|95|04|010",
        "OK05506|95|04|011",
        "OK05506|95|04|012",
        "OK05506|95|04|013",
        "OK05506|95|04|014",
        "OK05506|95|04|015",
        "OK05506|95|04|016",
        "OK05506|95|04|017",
        "OK05506|95|04|018",
        "OK05506|95|04|019",
        "OK05506|95|04|020",
        "OK05506|95|04|021",

        # 2017 Las Vegas shooting
        "NV00201|17|10|015",
        "NV00201|17|10|016",
        "NV00201|17|10|017",
        "NV00201|17|10|018",
        "NV00201|17|10|019",
        "NV00201|17|10|020",
    ]
    return (
        victims
        .loc[lambda df: ~df["incident_uid"].isin(incidents_to_exclude)]
    )

def load_shr_murder_victims():
    agency_metadata = load_shr_metadata()
    agency_metadata_2016 = load_shr_metadata_2016()

    victims = pd.read_csv(
        "../../data/standardized/shr-victims.csv"
    )

    victims["state"] = victims["agency_ori_7"].str.slice(0, 2)
    victims["state"].value_counts().tail()

    main_metadata_cols = [
        "year",
        "agency_ori_7",
        "ori_group",
        "larger_city",
    ]

    murder_victims = (
        victims
        .pipe(shr_remove_mass_murder_events)
        .loc[lambda df: df["top_offense_code"] == "09A"]
        .merge(
            agency_metadata[main_metadata_cols],
            how = "left",
            on = [ "agency_ori_7", "year" ]
        )
        .merge(
            agency_metadata_2016
            [main_metadata_cols]
            .drop(columns = [ "year" ]),
            how = "left",
            on = [ "agency_ori_7" ],
            suffixes = [ "_report", "_2016" ]
        )
        .assign(
            larger_city_2016 = lambda df: df["larger_city_2016"].fillna(False)
        )
    )

    return murder_victims

## NIBRS
def load_nibrs_metadata():
    return (
        pd.read_csv(
            "../../data/standardized/nibrs-agency-metadata.csv",
        )
        .assign(
            larger_city = lambda x: x["ori_group"].isin([
                "1A",
                "1B",
                "1C",
                "2"
            ])
        )
    )

def load_nibrs_metadata_2016():
    agency_metadata = load_nibrs_metadata()

    return (
        agency_metadata

        .loc[lambda df: df["year"] <= 2016]
        
        .sort_values("year", ascending = False)
        
        .drop_duplicates(subset = [ "agency_ori_9" ])
    )

def load_nibrs_victims():
    agency_metadata = load_nibrs_metadata()
    agency_metadata_2016 = load_nibrs_metadata_2016()

    main_metadata_cols = [
        "year",
        "agency_ori_9",
        "ori_group",
        "larger_city",
    ]

    victims = (
        pd.read_csv(
            "../../data/standardized/nibrs-victims.csv",
            dtype = {
                "top_offense_code": str,
            },
            parse_dates = [ "occurred_date", "arrest_date" ],
            date_parser = lambda x: pd.to_datetime(
                x,
                format = "%Y%m%d",
                errors = "coerce"
            )
        )
        .merge(
            agency_metadata
            [main_metadata_cols],
            on = [ "year", "agency_ori_9" ],
            how = "left"
        )
        .merge(
            agency_metadata_2016
            [main_metadata_cols]
            .drop(columns = [ "year" ]),
            on = [ "agency_ori_9" ],
            how = "left",
            suffixes = [ "_report", "_2016" ]
        )
    )

    victims["state"] = victims["agency_ori_9"].str.slice(0, 2)
    victims["state"].value_counts().tail()

    return victims
