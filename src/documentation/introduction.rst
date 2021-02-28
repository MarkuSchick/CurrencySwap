.. _introduction:


************
Introduction
************

The Project analyses the historical EURO/USD exchange rate to find parameters for a potential Currency Swap living on a blockchain.

We try various asset allocations and leverage factors to find a optimal design for such contract.
Competing designs can be easily added to the contracts folder and we can perform analyses for them.
Graphs are produced to visualize the relationship between historical EURO/USD volatility, contract parameterization
and (realized) payout. For this we take an backward perspective and simulated returns based on historical data of the EURO / USD exchange rate (1999-Today).

The aim is not to find a prediction of future of exchange rate movements, but show how the swap contract
would have payed out in the past.
The aim is to find the highest leverage factor available possible to pay out with a limited amount of collateral.
Background: Since financial claims can not be *enforced* on a blockchain we need to have hold collateral to full fill these claims.

They are exported to a short presentation and research paper.

.. _getting_started:

The project’s workflow
===============

The project follows the following steps:

1. Download data
2. Simulate 1-Year EURO/USD returns
3. Simulate payouts given Swap contract configurations
4. Research paper and presentations

Graphs are created along the way.