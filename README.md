# inbestment-portfolio
<a name="readme-top"></a>


<!-- TABLE OF CONTENTS -->
  ## Table of Contents ##
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#documentation-links">Documentation links</a></li>
    <li><a href="#solution-strategy">Solution strategy</a></li>
    <li><a href="#technologies">Technologies</a></li>
    <li><a href="#license">License</a></li>
  </ol>

<!-- ABOUT THE PROJECT -->
## About The Project
in**B**estmentPortfolio is a FinTech project [^1] aimed at defining the **best** investment portfolio by combining to a variable extent a given set of finacial indices, over a predefined time horizon.

[^1]: dating back to 2019 (during my masters's years)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Documentation links
* [Presentation slides](doc/presentation.pdf)[^2]
* [Project requirements text](doc/requirements.pdf)[^2]

[^2]: in Italian, as part of the project has been developed in the context of a university course tought in Italian that defined its requirements.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Solution strategy
The high-level solution strategy adopted consists in optimizing a trade-off between the estimated stock returns and the risk associated with a combination of the stock indices. This is accomplished by exploiting, among the others:
- **ARIMA** (GEP Box et al., [1976](http://scholar.google.com/scholar_lookup?&title=Time%20series%20analysis%3A%20forecasting%20and%20control&publication_year=1976&author=Box%2CGEP&author=Jenkins%2CGM&author=Reinsel%2CGC)) model, with some experiments ARIMA in rolling window mode along with some **decision tree** and **bagging** -based **regressor**s, leveraging **grid-search** for hyperparameter’s tuning, for *returns estimation*;
- both the **Volatility Weighted Historical Simulation** (John Hull et al., [1998](https://www.researchgate.net/profile/John-Hull-6/publication/2645882_Incorporating_volatility_updating_into_the_historical_simulation_method_for_VaR/links/00b7d5335d8e2394d0000000/Incorporating-volatility-updating-into-the-historical-simulation-method-for-VaR.pdf?_sg%5B0%5D=started_experiment_milestone&origin=journalDetail&_rtd=e30%3D)) and the **Filtered Historical Simulation** (Barone-Adesi et al., [1998](http://filteredhistoricalsimulation.com/downloads/paws_feb98.pdf)) approaches, for *risk estimation*;
- **GARCH** ([1986](https://www.sciencedirect.com/science/article/abs/pii/030440769290064X)) model, for conditional variance estimation, to support *risk estimation*;
- the **Differential Algorithm** (Rainer Storn et al., [1997](https://link.springer.com/article/10.1023/a:1008202821328)) metaheuristic and the **PSO** (James Kennedy et al., [1995](https://ieeexplore.ieee.org/abstract/document/488968/)) genetic algorithm, for *returns-risk trade-off optimization*.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Technologies

The project is implemented with:

* **Python**
* [.NET core](https://learn.microsoft.com/en-us/dotnet/core/introduction)
* [Entity Framework](https://learn.microsoft.com/en-us/ef/)
* [sklearn](https://scikit-learn.org/)
* [pmd-arima](https://pypi.org/project/pmdarima/)
* [arch](https://pypi.org/project/arch/)
* [sqlite](https://www.sqlite.org/index.html)





<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the GPL License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
