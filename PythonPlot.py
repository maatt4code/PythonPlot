from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe


class Side(Enum):
    BID = 1
    ASK = 2


class PriceLadder:
    min_increment = 0.00001
    base_half_spread = 2 * min_increment # 0.00001485622
    min_half_spread = min_increment
    skew_factor = 0.25 * min_increment

    def calc(x, pos: float):
        def px(side: Side) -> float:
            y =   0.00000000038 * x**6 \
                - 0.00000001183 * x**5 \
                + 0.00000014338 * x**4 \
                - 0.00000065763 * x**3 \
                + 0.00000067839 * x**2 \
                + 0.00000042125 * x \
                + PriceLadder.base_half_spread
            if side == Side.BID:
                y *= -1.0
            # skew
            if pos > 0:
                # Long, so need to sell => decrease bid and ask
                y -= pos * PriceLadder.skew_factor
            elif pos < 0:
                # Short, so need to buy => increase bid and ask
                y += pos * PriceLadder.skew_factor
            return y

        # get raw skewed prices based on position
        bid, ask = px(Side.BID), px(Side.ASK)
        # TODO - redistribute skew s.t. you prices do not cross mid
        if ask < PriceLadder.min_half_spread:
            diff = PriceLadder.min_half_spread - ask
            ask = PriceLadder.min_half_spread
            bid = bid - diff
        if bid > -1.0 * PriceLadder.min_half_spread:
            diff = bid - PriceLadder.min_half_spread
            bid = PriceLadder.min_half_spread
            ask = ask + diff
        return bid, ask

    def __init__(self):
        buckets = (10_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000, 200_000_000, 500_000_000, 1_000_000_000)
        self.position = 0
        # create df with zeros
        feature_list = ["id", "bucket", "bid_px", "ask_px"]
        self.df = pd.DataFrame(0, index=np.arange(len(buckets)), columns=feature_list)
        self.df["id"] = np.arange(len(buckets))
        self.df["bucket"] = buckets
        self.calc_ladder(0)
        pass

    def calc_ladder(self, pos: float) -> None:
        self.df["bid_px"], self.df["ask_px"] = zip(*self.df["id"].apply(lambda x: PriceLadder.calc(x, pos)))

    def set_position(self, pos: float):
        self.calc_ladder(pos)
        pass

    def plot(self, xticks_col):
        print(self.df)

        # clear plot
        plt.clf()

        # plot the lines
        x = self.df[xticks_col]
        plt.plot(x, self.df["ask_px"], color='r', linewidth=4, path_effects=[pe.Stroke(linewidth=5, foreground='k'), pe.Normal()])
        plt.plot(x, self.df["bid_px"], color='b', linewidth=4, path_effects=[pe.Stroke(linewidth=5, foreground='k'), pe.Normal()])

        # shift x-axis to middle. clean other axis
        ax = plt.gca()
        ax.spines['bottom'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        # Remove ticks, add labels
        plt.xticks([]), ax.set_xlabel(xticks_col, loc='right')
        # plt.yticks([]), ax.set_ylabel('Price', loc='top')
        plt.yticks([]), ax.set_ylabel('Mid', loc='center')

        # plot / save
        plt.show()
        plt.clf()


def main():
    print("Hello")
    ladder = PriceLadder()
    ladder.plot("id")
    ladder.plot("bucket")
    for pos in range(1, 50, 5):
        ladder.set_position(pos)
        ladder.plot("bucket")


if __name__ == "__main__":
    main()
