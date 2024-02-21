from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe


class Side(Enum):
    BID = 1
    ASK = 2


class PriceLadder:
    base_spread = 0.00002 # 0.00001485622
    min_spread = 0.00001

    @staticmethod
    def calc(x, pos: float, side: Side) -> float:
        if side == Side.BID:
            y =   0.00000000038 * x**6 \
                - 0.00000001183 * x**5 \
                + 0.00000014338 * x**4 \
                - 0.00000065763 * x**3 \
                + 0.00000067839 * x**2 \
                + 0.00000042125 * x \
                + PriceLadder.base_spread
            y *= -1.0
        else:
            y =   0.00000000038 * x**6 \
                - 0.00000001183 * x**5 \
                + 0.00000014338 * x**4 \
                - 0.00000065763 * x**3 \
                + 0.00000067839 * x**2 \
                + 0.00000042125 * x \
                + PriceLadder.base_spread

        return y

    def __init__(self):
        buckets = (10_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000, 200_000_000, 500_000_000, 1_000_000_000)
        self.position = 0
        # create df with zeros
        feature_list = ["id", "bucket", "bid_px", "ask_px"]
        self.df = pd.DataFrame(0, index=np.arange(len(buckets)), columns=feature_list)
        self.df["id"] = np.arange(len(buckets))
        self.df["bucket"] = buckets
        self.df["bid_px"] = self.df["id"].apply(lambda x: PriceLadder.calc(x, 0, Side.BID))
        self.df["ask_px"] = self.df["id"].apply(lambda x: PriceLadder.calc(x, 0, Side.ASK))
        pass

    def add_position(self, pos):
        # apply skew, recalc ladders
        pass

    def plot(self, xticks_col):
        # clear plot
        plt.clf()

        # plot the lines
        x = self.df[xticks_col]
        plt.plot(x, self.df["ask_px"], color='r', linewidth=4, path_effects=[pe.Stroke(linewidth=5, foreground='k'), pe.Normal()])
        plt.plot(x, self.df["bid_px"], color='b', linewidth=4, path_effects=[pe.Stroke(linewidth=5, foreground='k'), pe.Normal()])

        # shift x-axis to middle. clean other axis
        ax = plt.gca()
        ax.spines['bottom'].set_position('center')        
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        # Remove ticks, add labels
        plt.xticks([]), ax.set_xlabel(xticks_col, loc='right')
        plt.yticks([]), ax.set_ylabel('Price', loc='top')

        # plot / save
        plt.show()
        #plt.clf()


def main():
    print("Hello")
    ladder = PriceLadder()
    ladder.plot("id")
    ladder.plot("bucket")


if __name__ == "__main__":
    main()