from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.animation as animation


class Side(Enum):
    BID = 1
    ASK = 2


class PriceLadder:
    min_increment = 0.00001
    base_half_spread = 100 * min_increment # 0.00001485622, #+ 1.0000025490630
    skew_factor = 10 * min_increment

    def calc(x, half_spread, pos: float):
        def px(side: Side) -> float:
            y = - 0.0000000000001 * x**8 \
                + 0.0000000000175 * x**7 \
                - 0.0000000008594 * x**6 \
                + 0.0000000223001 * x**5 \
                - 0.0000003291554 * x**4 \
                + 0.0000027520073 * x**3 \
                - 0.0000118604919 * x**2 \
                + 0.0000216921451 * x    \
                + PriceLadder.base_half_spread
            if side == Side.BID:
                y *= -1.0
            # skew
            y -= pos * PriceLadder.skew_factor
            return y

        # get raw skewed prices based on position
        bid, ask = px(Side.BID), px(Side.ASK)
        # TODO - redistribute skew s.t. you prices do not cross mid
        if ask < PriceLadder.base_half_spread:
            diff = min(abs(PriceLadder.base_half_spread - ask), half_spread) - PriceLadder.base_half_spread
            ask = PriceLadder.base_half_spread
            bid = max(bid - diff - 2 * PriceLadder.base_half_spread, - 2 * (half_spread + PriceLadder.base_half_spread))
        if bid > - PriceLadder.base_half_spread:
            diff = min(abs(PriceLadder.base_half_spread -bid), half_spread) + PriceLadder.base_half_spread
            bid = - PriceLadder.base_half_spread
            ask = min(ask + diff + 2 * PriceLadder.base_half_spread, 2 * (half_spread + PriceLadder.base_half_spread))
        # maintain minimum spread
        if abs(ask - bid) < 2.0 * PriceLadder.base_half_spread:
            diff = 2.0 * PriceLadder.base_half_spread - abs(ask - bid)
            if pos < 0:
                bid -= diff
            else:
                ask += diff
        return bid, ask

    def __init__(self):
        buckets = (1, 2, 3, 4, 5, 6, 7.75, 10, 13, 17, 21.5, 27)
        self.fig, self.ax = plt.subplots()
        self.frames = []
        self._init_plot()
        # create df with zeros
        feature_list = ["bucket", "half_spread", "bid_px", "ask_px"]
        self.df = pd.DataFrame(0, index=np.arange(len(buckets)), columns=feature_list)
        self.df["bucket"] = buckets
        self._calc_ladder(0)
        self.df["half_spread"] = (self.df["ask_px"] - self.df["bid_px"]) / 2.0
        pass

    def _init_plot(self):
        self.fig.tight_layout()

        # shift x-axis to middle. clean other axis
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')

        # Remove ticks, add labels
        self.ax.xaxis.set_ticks([]), self.ax.set_xlabel("bucket", loc='right')
        # plt.yticks([]), ax.set_ylabel('Price', loc='top')
        self.ax.yaxis.set_ticks([]), self.ax.set_ylabel('Mid', loc='center')

    def set_position(self, pos: float):
        self._calc_ladder(pos)
        self._add_plot()
        pass

    def _calc_ladder(self, pos: float) -> None:
        self.df["bid_px"], self.df["ask_px"] = zip(*self.df.apply(lambda x: PriceLadder.calc(x["bucket"], x["half_spread"], pos), axis=1))
        #print(self.df.apply(lambda x: PriceLadder.calc(x["bucket"], x["half_spread"], pos), axis=1))

    def _add_plot(self):
        #print(self.df)

        # plot the lines in the same plot so we can save it for animation
        x = self.df["bucket"]
        pix = self.ax.plot(
            x, self.df["ask_px"], 'r',
            x, self.df["bid_px"], 'b',
            linewidth=4, path_effects=[pe.Stroke(linewidth=5, foreground='k'), pe.Normal()])

        self.frames.append(pix)


def main():
    print("Hello")
    ladder = PriceLadder()
    for pos in range(1, 50, 5):
        ladder.set_position(pos)
    for pos in range(50, 1, -5):
        ladder.set_position(pos)
    for pos in range(-1, -50, -5):
        ladder.set_position(pos)
    for pos in range(-50, -1, 5):
        ladder.set_position(pos)
    anim = animation.ArtistAnimation(fig=ladder.fig, artists=ladder.frames, interval=200)
    anim.save(filename="pillow_example.gif", writer="pillow")
    #plt.show()


if __name__ == "__main__":
    main()
