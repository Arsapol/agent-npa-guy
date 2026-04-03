#!/usr/bin/env python3
"""Thai NPA property financial calculator.

Calculates acquisition costs, rental yield, price per area,
and break-even timeline for Thai real estate.
"""

import argparse
import json
import sys


# Thai real estate transaction costs
TRANSFER_FEE_RATE = 0.02          # 2% of appraised value
SPECIFIC_BUSINESS_TAX_RATE = 0.033  # 3.3% (if held < 5 years)
STAMP_DUTY_RATE = 0.005           # 0.5% (if held >= 5 years, mutually exclusive with SBT)
WITHHOLDING_TAX_RATE = 0.01       # 1% of appraised or selling price (whichever higher)

# LED auction price reduction schedule (กรมบังคับคดี)
# นัดที่ 1: 100% of appraised/committee price
# นัดที่ 2: 90% (if unsold)
# นัดที่ 3: 80% (if unsold)
# นัดที่ 4+: 70% floor (won't go lower)
LED_AUCTION_RATES = {
    1: 1.00,
    2: 0.90,
    3: 0.80,
}
LED_FLOOR_RATE = 0.70  # นัดที่ 4 เป็นต้นไป
LED_FLOOR_ROUND = 4    # Round at which floor kicks in

# Size conversions
SQM_PER_WAH = 4.0
SQM_PER_NGAN = 400.0
SQM_PER_RAI = 1600.0


def to_sqm(rai=0, ngan=0, wah=0, sqm=0):
    """Convert Thai land units to square meters."""
    return (rai * SQM_PER_RAI) + (ngan * SQM_PER_NGAN) + (wah * SQM_PER_WAH) + sqm


def led_round_rate(round_number):
    """Get the auction price rate for a given LED round.

    Rules (กรมบังคับคดี):
      นัดที่ 1: 100% of appraised price
      นัดที่ 2: 90%
      นัดที่ 3: 80%
      นัดที่ 4+: 70% (floor, never goes lower)
    """
    if round_number < 1:
        raise ValueError(f"Round number must be >= 1, got {round_number}")
    if round_number >= LED_FLOOR_ROUND:
        return LED_FLOOR_RATE
    return LED_AUCTION_RATES[round_number]


def led_auction_price(appraised_price, round_number):
    """Calculate expected auction price at a given LED round.

    Returns the starting bid price for that round.
    """
    rate = led_round_rate(round_number)
    return appraised_price * rate


def led_is_at_floor(round_number):
    """Check if the auction round is already at the floor price (70%)."""
    return round_number >= LED_FLOOR_ROUND


def led_analysis(appraised_price, current_round):
    """Full LED auction analysis showing all rounds and current position.

    Returns dict with price schedule, current status, and remaining discount.
    """
    current_rate = led_round_rate(current_round)
    current_price = appraised_price * current_rate
    at_floor = led_is_at_floor(current_round)

    # Calculate all rounds
    max_round = max(current_round + 2, LED_FLOOR_ROUND + 1)
    schedule = []
    for r in range(1, max_round + 1):
        rate = led_round_rate(r)
        schedule.append({
            "round": r,
            "rate_pct": round(rate * 100, 1),
            "price": round(appraised_price * rate, 2),
            "is_current": r == current_round,
            "is_floor": rate == LED_FLOOR_RATE,
        })

    return {
        "appraised_price": appraised_price,
        "current_round": current_round,
        "current_rate_pct": round(current_rate * 100, 1),
        "current_starting_price": round(current_price, 2),
        "at_floor": at_floor,
        "floor_rate_pct": round(LED_FLOOR_RATE * 100, 1),
        "floor_price": round(appraised_price * LED_FLOOR_RATE, 2),
        "max_discount_from_appraisal_pct": round((1 - LED_FLOOR_RATE) * 100, 1),
        "can_go_lower": not at_floor,
        "next_round_price": round(appraised_price * led_round_rate(current_round + 1), 2) if not at_floor else None,
        "schedule": schedule,
    }


def acquisition_cost(
    purchase_price,
    appraised_value=None,
    held_under_5_years=True,
    buyer_pays_transfer=True,
    buyer_pays_tax=False,
    renovation_cost=0,
):
    """Calculate total acquisition cost breakdown.

    In Thai NPA auctions, typically:
    - Buyer pays transfer fee (2%)
    - Seller (bank/court) pays SBT or stamp duty + WHT
    But in practice, NPA buyers often negotiate or absorb all costs.
    """
    if appraised_value is None:
        appraised_value = purchase_price

    base = max(purchase_price, appraised_value)

    transfer_fee = base * TRANSFER_FEE_RATE
    withholding_tax = base * WITHHOLDING_TAX_RATE

    if held_under_5_years:
        specific_business_tax = base * SPECIFIC_BUSINESS_TAX_RATE
        stamp_duty = 0
    else:
        specific_business_tax = 0
        stamp_duty = base * STAMP_DUTY_RATE

    # What buyer actually pays
    buyer_transfer = transfer_fee if buyer_pays_transfer else 0
    buyer_tax = (specific_business_tax + stamp_duty + withholding_tax) if buyer_pays_tax else 0

    total_buyer_costs = buyer_transfer + buyer_tax + renovation_cost
    total_acquisition = purchase_price + total_buyer_costs

    return {
        "purchase_price": purchase_price,
        "appraised_value": appraised_value,
        "discount_pct": round((1 - purchase_price / appraised_value) * 100, 1) if appraised_value > 0 else 0,
        "transfer_fee": round(transfer_fee, 2),
        "specific_business_tax": round(specific_business_tax, 2),
        "stamp_duty": round(stamp_duty, 2),
        "withholding_tax": round(withholding_tax, 2),
        "total_transfer_costs": round(transfer_fee + specific_business_tax + stamp_duty + withholding_tax, 2),
        "buyer_pays_transfer_fee": round(buyer_transfer, 2),
        "buyer_pays_taxes": round(buyer_tax, 2),
        "renovation_cost": renovation_cost,
        "total_buyer_costs": round(total_buyer_costs, 2),
        "total_acquisition_cost": round(total_acquisition, 2),
    }


def rental_yield(
    purchase_price,
    monthly_rent,
    vacancy_rate=0.10,
    management_fee_pct=0.05,
    maintenance_monthly=0,
    common_fee_monthly=0,
):
    """Calculate rental yield metrics."""
    annual_gross_rent = monthly_rent * 12
    effective_rent = annual_gross_rent * (1 - vacancy_rate)

    annual_management = annual_gross_rent * management_fee_pct
    annual_maintenance = maintenance_monthly * 12
    annual_common_fee = common_fee_monthly * 12
    annual_expenses = annual_management + annual_maintenance + annual_common_fee

    net_annual_income = effective_rent - annual_expenses

    gross_yield = (annual_gross_rent / purchase_price * 100) if purchase_price > 0 else 0
    net_yield = (net_annual_income / purchase_price * 100) if purchase_price > 0 else 0

    return {
        "monthly_rent": monthly_rent,
        "annual_gross_rent": annual_gross_rent,
        "vacancy_rate_pct": vacancy_rate * 100,
        "effective_annual_rent": round(effective_rent, 2),
        "annual_expenses": round(annual_expenses, 2),
        "net_annual_income": round(net_annual_income, 2),
        "gross_yield_pct": round(gross_yield, 2),
        "net_yield_pct": round(net_yield, 2),
        "break_even_years": round(purchase_price / net_annual_income, 1) if net_annual_income > 0 else None,
        "monthly_cash_flow": round(net_annual_income / 12, 2),
    }


def rent_range_analysis(
    purchase_price,
    rent_low=None,
    rent_mid=None,
    rent_high=None,
    vacancy_rate=0.10,
    common_fee_monthly=0,
):
    """Run rental yield analysis for LOW/MID/HIGH rent scenarios.

    Forces analyst to show the full range instead of cherry-picking optimistic rent.
    """
    scenarios = {}
    if rent_low:
        scenarios["LOW"] = rental_yield(purchase_price, rent_low, vacancy_rate=vacancy_rate, common_fee_monthly=common_fee_monthly)
    if rent_mid:
        scenarios["MID"] = rental_yield(purchase_price, rent_mid, vacancy_rate=vacancy_rate, common_fee_monthly=common_fee_monthly)
    if rent_high:
        scenarios["HIGH"] = rental_yield(purchase_price, rent_high, vacancy_rate=vacancy_rate, common_fee_monthly=common_fee_monthly)
    return scenarios


def price_per_area(purchase_price, rai=0, ngan=0, wah=0, sqm=0):
    """Calculate price per various area units."""
    total_sqm = to_sqm(rai, ngan, wah, sqm)
    total_wah = total_sqm / SQM_PER_WAH

    result = {
        "total_sqm": round(total_sqm, 2),
        "total_wah": round(total_wah, 2),
    }

    if total_sqm > 0:
        result["price_per_sqm"] = round(purchase_price / total_sqm, 2)
        result["price_per_wah"] = round(purchase_price / total_wah, 2)

    if total_sqm >= SQM_PER_RAI:
        total_rai = total_sqm / SQM_PER_RAI
        result["total_rai"] = round(total_rai, 2)
        result["price_per_rai"] = round(purchase_price / total_rai, 2)

    return result


def full_analysis(
    purchase_price,
    appraised_value=None,
    monthly_rent=None,
    rai=0, ngan=0, wah=0, sqm=0,
    renovation_cost=0,
    held_under_5_years=True,
    vacancy_rate=0.10,
    common_fee_monthly=0,
    rent_low=None,
    rent_mid=None,
    rent_high=None,
    market_price_per_sqm=None,
):
    """Run full financial analysis combining all calculations."""
    result = {"purchase_price": purchase_price}

    # Acquisition costs
    result["acquisition"] = acquisition_cost(
        purchase_price, appraised_value,
        held_under_5_years=held_under_5_years,
        renovation_cost=renovation_cost,
    )

    # Price per area
    total_sqm = to_sqm(rai, ngan, wah, sqm)
    if total_sqm > 0:
        result["area"] = price_per_area(purchase_price, rai, ngan, wah, sqm)

    # Discount sanity check vs market
    if market_price_per_sqm and total_sqm > 0:
        ppsqm = purchase_price / total_sqm
        result["discount_check"] = discount_sanity_check(ppsqm, market_price_per_sqm)

    # Rental yield (single rent)
    if monthly_rent and monthly_rent > 0:
        result["rental"] = rental_yield(
            result["acquisition"]["total_acquisition_cost"],
            monthly_rent,
            vacancy_rate=vacancy_rate,
            common_fee_monthly=common_fee_monthly,
        )

    # Rental yield range (LOW/MID/HIGH)
    if rent_low or rent_mid or rent_high:
        result["rent_range"] = rent_range_analysis(
            result["acquisition"]["total_acquisition_cost"],
            rent_low=rent_low,
            rent_mid=rent_mid,
            rent_high=rent_high,
            vacancy_rate=vacancy_rate,
            common_fee_monthly=common_fee_monthly,
        )

    return result


def format_thb(amount):
    """Format as Thai Baht."""
    if amount is None:
        return "N/A"
    if amount >= 1_000_000:
        return f"฿{amount:,.0f} ({amount / 1_000_000:.2f}M)"
    return f"฿{amount:,.0f}"


def discount_sanity_check(price_per_sqm, market_per_sqm, area_name=""):
    """Warn if the claimed discount vs market is suspiciously large.

    Real NPA discounts are typically 15-35%. Anything >50% needs verification.
    """
    if not market_per_sqm or market_per_sqm <= 0 or not price_per_sqm or price_per_sqm <= 0:
        return None

    discount_pct = (1 - price_per_sqm / market_per_sqm) * 100
    result = {
        "price_per_sqm": price_per_sqm,
        "market_per_sqm": market_per_sqm,
        "discount_pct": round(discount_pct, 1),
        "warning": None,
    }

    if discount_pct > 50:
        result["warning"] = (
            f"⚠️  SKEPTICISM ALERT: {discount_pct:.0f}% below market ({area_name}). "
            f"Real NPA discounts are usually 15-35%. VERIFY data units, building identity, "
            f"and market comp before trusting this number."
        )
    elif discount_pct > 35:
        result["warning"] = (
            f"⚠️  Double-check: {discount_pct:.0f}% below market is possible but on the high end. "
            f"Verify market comp and property condition."
        )

    return result


def print_analysis(result):
    """Pretty-print full analysis."""
    print(f"\n{'='*60}")
    print(f"NPA PROPERTY FINANCIAL ANALYSIS")
    print(f"{'='*60}")

    acq = result.get("acquisition", {})
    print(f"\n--- Acquisition Costs ---")
    print(f"  Purchase Price:     {format_thb(acq.get('purchase_price'))}")
    print(f"  Appraised Value:    {format_thb(acq.get('appraised_value'))}")
    print(f"  Discount:           {acq.get('discount_pct', 0)}%")
    print(f"  Transfer Fee (2%):  {format_thb(acq.get('transfer_fee'))}")
    print(f"  SBT (3.3%):         {format_thb(acq.get('specific_business_tax'))}")
    print(f"  Stamp Duty (0.5%):  {format_thb(acq.get('stamp_duty'))}")
    print(f"  WHT (1%):           {format_thb(acq.get('withholding_tax'))}")
    print(f"  Renovation:         {format_thb(acq.get('renovation_cost'))}")
    print(f"  ─────────────────────────────")
    print(f"  Buyer Pays:         {format_thb(acq.get('total_buyer_costs'))}")
    print(f"  TOTAL ACQUISITION:  {format_thb(acq.get('total_acquisition_cost'))}")

    area = result.get("area")
    if area:
        print(f"\n--- Price per Area ---")
        print(f"  Total Area:         {area.get('total_sqm', 0):.1f} sqm ({area.get('total_wah', 0):.1f} wah)")
        if "price_per_sqm" in area:
            print(f"  Price/sqm:          {format_thb(area['price_per_sqm'])}")
        if "price_per_wah" in area:
            print(f"  Price/wah:          {format_thb(area['price_per_wah'])}")
        if "price_per_rai" in area:
            print(f"  Price/rai:          {format_thb(area['price_per_rai'])}")

    rental = result.get("rental")
    if rental:
        print(f"\n--- Rental Yield ---")
        print(f"  Monthly Rent:       {format_thb(rental.get('monthly_rent'))}")
        print(f"  Vacancy:            {rental.get('vacancy_rate_pct', 10)}%")
        print(f"  Net Annual Income:  {format_thb(rental.get('net_annual_income'))}")
        print(f"  Gross Yield:        {rental.get('gross_yield_pct', 0)}%")
        print(f"  Net Yield:          {rental.get('net_yield_pct', 0)}%")
        print(f"  Monthly Cash Flow:  {format_thb(rental.get('monthly_cash_flow'))}")
        be = rental.get("break_even_years")
        print(f"  Break-even:         {f'{be} years' if be else 'N/A'}")

    rent_range = result.get("rent_range")
    if rent_range:
        print(f"\n--- Rent Range Scenarios (LOW / MID / HIGH) ---")
        print(f"  {'Scenario':<10} {'Rent/mo':>12} {'Gross':>8} {'Net':>8} {'Break-even':>12} {'Cash Flow/mo':>14}")
        print(f"  {'─'*10} {'─'*12} {'─'*8} {'─'*8} {'─'*12} {'─'*14}")
        for label, data in rent_range.items():
            be = data.get("break_even_years")
            be_str = f"{be} yrs" if be else "N/A"
            print(f"  {label:<10} {format_thb(data['monthly_rent']):>12} {data['gross_yield_pct']:>7.1f}% {data['net_yield_pct']:>7.1f}% {be_str:>12} {format_thb(data['monthly_cash_flow']):>14}")
        if len(rent_range) >= 2:
            low_data = list(rent_range.values())[0]
            high_data = list(rent_range.values())[-1]
            yield_spread = high_data['net_yield_pct'] - low_data['net_yield_pct']
            print(f"\n  ⚠️  Yield spread: {yield_spread:.1f}pp between LOW and HIGH — consider which scenario is realistic")

    discount = result.get("discount_check")
    if discount:
        print(f"\n--- Market Discount Sanity Check ---")
        print(f"  NPA Price/sqm:      ฿{discount['price_per_sqm']:,.0f}")
        print(f"  Market Price/sqm:   ฿{discount['market_per_sqm']:,.0f}")
        print(f"  Discount:           {discount['discount_pct']:.1f}%")
        if discount["warning"]:
            print(f"\n  {discount['warning']}")

    print(f"\n{'='*60}\n")


def print_led_analysis(led):
    """Pretty-print LED auction analysis."""
    print(f"\n{'='*60}")
    print(f"LED AUCTION PRICE ANALYSIS (กรมบังคับคดี)")
    print(f"{'='*60}")
    print(f"\n  Appraised Price:    {format_thb(led['appraised_price'])}")
    print(f"  Current Round:      นัดที่ {led['current_round']}")

    if led['at_floor']:
        print(f"  ⚠️  AT FLOOR PRICE — cannot go lower")
    else:
        print(f"  ✅ Not at floor yet — price may drop further")
        print(f"     Next round (นัดที่ {led['current_round']+1}): {format_thb(led['next_round_price'])}")

    print(f"\n  Current Rate:       {led['current_rate_pct']}% of appraisal")
    print(f"  Current Price:      {format_thb(led['current_starting_price'])}")
    print(f"  Floor Rate:         {led['floor_rate_pct']}% (from นัดที่ {LED_FLOOR_ROUND}+)")
    print(f"  Floor Price:        {format_thb(led['floor_price'])}")
    print(f"  Max Discount:       {led['max_discount_from_appraisal_pct']}% off appraisal")

    print(f"\n  --- Price Schedule ---")
    for s in led['schedule']:
        marker = " ◀ CURRENT" if s['is_current'] else ""
        floor_tag = " (floor)" if s['is_floor'] and not s['is_current'] else ""
        print(f"  นัดที่ {s['round']}: {s['rate_pct']:>5.1f}% = {format_thb(s['price'])}{marker}{floor_tag}")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Thai NPA Property Financial Calculator")
    parser.add_argument("--price", type=float, required=False, help="Purchase price (baht)")
    parser.add_argument("--appraised", type=float, help="Appraised value (baht)")
    parser.add_argument("--rent", type=float, help="Expected monthly rent (baht)")
    parser.add_argument("--rent-low", type=float, help="Low rent estimate (baht/month)")
    parser.add_argument("--rent-mid", type=float, help="Mid rent estimate (baht/month)")
    parser.add_argument("--rent-high", type=float, help="High rent estimate (baht/month)")
    parser.add_argument("--market-price", type=float, help="Market price per sqm/wah for discount sanity check")
    parser.add_argument("--market-unit", choices=["sqm", "wah"], default="sqm", help="Unit for --market-price (default: sqm)")
    parser.add_argument("--rai", type=float, default=0)
    parser.add_argument("--ngan", type=float, default=0)
    parser.add_argument("--wah", type=float, default=0)
    parser.add_argument("--sqm", type=float, default=0, help="Size in sqm (for condos). NOTE: if querying from DB, the 'size_wa' column for ห้องชุด is already in sqm, pass it here directly.")
    parser.add_argument("--renovation", type=float, default=0, help="Renovation cost (baht)")
    parser.add_argument("--vacancy", type=float, default=0.10, help="Vacancy rate (default: 0.10)")
    parser.add_argument("--common-fee", type=float, default=0, help="Monthly common area fee (baht)")
    parser.add_argument("--held-over-5y", action="store_true", help="Property held over 5 years (stamp duty instead of SBT)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--led-round", type=int, help="LED auction round number (shows price reduction analysis)")
    parser.add_argument("--led-appraised", type=float, help="Appraised price for LED analysis (defaults to --appraised)")

    args = parser.parse_args()

    # Resolve market price per sqm
    market_ppsqm = None
    if args.market_price and args.market_price > 0:
        if args.market_unit == "sqm":
            market_ppsqm = args.market_price
        else:  # wah
            market_ppsqm = args.market_price / SQM_PER_WAH  # convert price/wah to price/sqm

    # LED auction analysis mode
    if args.led_round:
        led_appraised = args.led_appraised or args.appraised or args.price
        if not led_appraised:
            parser.error("--led-round requires --led-appraised, --appraised, or --price")

        led_result = led_analysis(led_appraised, args.led_round)

        if args.json:
            print(json.dumps(led_result, ensure_ascii=False, indent=2))
        else:
            print_led_analysis(led_result)

        # If price is also given, run full analysis
        if args.price and args.price != led_appraised:
            result = full_analysis(
                purchase_price=args.price,
                appraised_value=args.appraised,
                monthly_rent=args.rent,
                rai=args.rai, ngan=args.ngan, wah=args.wah, sqm=args.sqm,
                renovation_cost=args.renovation,
                held_under_5_years=not args.held_over_5y,
                vacancy_rate=args.vacancy,
                common_fee_monthly=args.common_fee,
                rent_low=args.rent_low, rent_mid=args.rent_mid, rent_high=args.rent_high,
                market_price_per_sqm=market_ppsqm,
            )
            if not args.json:
                print_analysis(result)
        return

    if not args.price:
        parser.error("--price is required (unless using --led-round)")

    result = full_analysis(
        purchase_price=args.price,
        appraised_value=args.appraised,
        monthly_rent=args.rent,
        rai=args.rai, ngan=args.ngan, wah=args.wah, sqm=args.sqm,
        renovation_cost=args.renovation,
        held_under_5_years=not args.held_over_5y,
        vacancy_rate=args.vacancy,
        common_fee_monthly=args.common_fee,
        rent_low=args.rent_low, rent_mid=args.rent_mid, rent_high=args.rent_high,
        market_price_per_sqm=market_ppsqm,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_analysis(result)


if __name__ == "__main__":
    main()
