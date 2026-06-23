# Domain Notes

Background for the trader-workstation-platform data model. The infrastructure
is the real subject of this project; these notes keep the finance vocabulary
honest so the data model reflects how the Anvil Platform's world actually works.

## Repo (repurchase agreement)

A repo is a short-term secured loan dressed as a sale. A party that needs cash
sells a security — typically a government bond — to a counterparty and
simultaneously agrees to buy it back later at a slightly higher price. The price
difference is effectively interest, called the repo rate. Economically the cash
lender is making a collateralised loan: if the borrower fails to repay, the lender
keeps the bond. The mirror trade, seen from the cash lender's side, is a reverse
repo. Repos are driven by the need for cash (or, on the other side, a safe
short-term place to park it), not by interest in the security itself.

## Securities lending

Securities lending is driven by the need for a *specific security* rather than
cash. One party (the lender, often a long-term holder like a pension fund) lends
a particular bond or share to a borrower — frequently a party that has sold that
security short and must deliver it. In return the borrower posts collateral, and
crucially that collateral is usually worth *more* than the lent security
(over-collateralisation), which protects the lender if the borrower defaults. The
borrower pays a lending fee for the privilege. At the end of the loan the security
comes back and the collateral is returned.

## What "position" means here

A position is the state of a single open trade — what you're holding, against
whom, and on what terms. For a repo, that means the security pledged as collateral,
the cash amount, the counterparty, the repo rate, and the start and maturity dates.
For securities lending, it means the security on loan, the collateral held against
it, the counterparty, the fee, and the loan's start and return dates. Both share a
settlement status (has the exchange of cash and security actually completed, or is
it still pending), which is why the data model treats a position as a richer object
than a simple symbol-and-quantity row — every one of those fields is something an
ops team might need to see on a screen to know where a trade stands.

## Settlement status

Settlement status tracks whether a trade has actually moved from an agreement
on paper into a completed exchange of cash and securities. A booked trade sits
as PENDING until the counterparty's cash and your security (or vice versa) both
actually change hands on the agreed value date; once that exchange clears, the
trade becomes SETTLED and the position is real on the book. If the exchange
doesn't happen by the expected date — most commonly because the seller doesn't
actually have the security to deliver — the trade is marked FAILED, a
"settlement fail." Ops teams watch this status closely: a PENDING trade still
carries counterparty risk (you haven't received what you contracted for), and a
FAILED trade can cascade — it may leave you unable to deliver a security you've
separately promised to someone else, trigger compensation costs, and draw
regulatory attention, since settlement fail rates are tracked as a sign of
operational health.