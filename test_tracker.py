from datetime import date, timedelta

from tracker import analyze, event_results, find_price, parse_price

for raw, want in [("Rs. 1,299.00", 1299.0), ("$19.99", 19.99), ("1.299,00 €", 1299.0), ("12,50", 12.5),
                  ("1,299", 1299.0), (19.99, 19.99), ("Sold out", None)]:
    assert parse_price(raw) == want, (raw, parse_price(raw))

ld = '<script type="application/ld+json">{"@graph":[{"@type":"Org"},{"@type":"Product","offers":{"price":"49.50"}}]}</script>'
assert find_price(ld) == 49.5
assert find_price('<script type="application/ld+json">[{"offers":[{"lowPrice":9}]}]</script>') == 9
assert find_price('<script type="application/ld+json">{bad json</script><meta property="og:price:amount" content="7.25">') == 7.25
assert find_price('<span class="p">£ 5.00</span>', ".p") == 5.0
assert find_price("<html></html>") is None

D0 = date(2026, 1, 1)


def mk(*segs, was=None):
    """mk((60, 100), (1, 70)) = 60 days at 100 then today at 70 (last segment is today)."""
    s, d = [], D0
    for n, p in segs:
        for _ in range(n):
            s.append((d, p, None))
            d += timedelta(1)
    if was:
        s[-1] = (s[-1][0], s[-1][1], was)
    return s


def verdict(*segs, was=None):
    return analyze(mk(*segs, was=was))


assert verdict((5, 100), (1, 80))["verdict"] == "learning"
assert verdict((75, 100), (1, 70))["verdict"] == "real deal"
assert verdict((75, 100), (1, 101))["verdict"] == "normal"
assert verdict((75, 100), (1, 120))["verdict"] == "pricey"

# raised 30% for 15 days, then "sale" back to normal -> gimmick
a = verdict((60, 100), (15, 130), (1, 100))
assert a["verdict"] == "gimmick" and "raised" in a["reasons"][0], a

# 'was' price that was never charged -> gimmick; same for a permanent sale
assert verdict((75, 100), (1, 95), was=200)["verdict"] == "gimmick"
assert verdict((75, 70), (1, 70), was=100)["verdict"] == "gimmick"

# modest discount, cheaper two weeks ago -> decent, with a note about the cheaper day
a = verdict((60, 100), (10, 80), (10, 100), (1, 92))
assert a["verdict"] == "decent" and any("cheaper" in r for r in a["reasons"]), a

# genuine deal with an honest 'was' price stays a real deal
assert verdict((75, 100), (1, 70), was=100)["verdict"] == "real deal"

# event scorecard: 60 days at 100, then event days at 100 (no discount) vs 80 (real)
flat, deep = mk((64, 100)), mk((60, 100), (4, 80))
ev = event_results([{"name": "BF", "start": (D0 + timedelta(60)).isoformat(), "end": (D0 + timedelta(63)).isoformat()}],
                   {("a", "x"): flat, ("a", "y"): deep, ("a", "z"): mk((3, 100))})
off = {r["shop"]: r["off"] for r in ev[0]["results"]}
assert off == {"x": 0.0, "y": 0.2}, off  # 'z' has too little history before the event, skipped
print("ok")
