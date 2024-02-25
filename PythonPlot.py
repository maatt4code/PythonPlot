from enum import Enum
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.animation as animation
import matplotlib.patches as patches


class Side(Enum):
    BID = 1
    ASK = 2


class Pricer:
    buckets = (1, 2, 3, 4, 5, 6, 7.75, 10, 13, 17, 21.5, 27)
    min_increment = 0.00001
    min_half_spread = 2 * min_increment
    skew_factor = 1 * min_increment

    def __init__(self) -> None:
        pass

    def calc(self, x, half_spread, pos: float):
        def px(side: Side) -> float:
            MID = 0.0
            def px_1() -> float:
                y = - 0.0000000000001 * x**8 + 0.0000000000175 * x**7 - 0.0000000008594 * x**6 + 0.0000000223001 * x**5 \
                    - 0.0000003291554 * x**4 + 0.0000027520073 * x**3 - 0.0000118604919 * x**2 + 0.0000216921451 * x
                return y
            def px_2() -> float:
                y = - 0.00000000000015 * x**8 + 0.00000000001854 * x**7 - 0.00000000093137 * x**6 + 0.00000002458305 * x**5 \
                    - 0.00000036604094 * x**4 + 0.00000304957510 * x**3 - 0.00001277979671 * x**2 + 0.00002077498199 * x
                return y
            # calculate price for bucket
            y = px_2()
            # apply spread
            if side == Side.ASK:
                y += Pricer.min_half_spread
            else:
                y *= -1.0
                y -= Pricer.min_half_spread
            # shift to mid
            y += MID
            # apply skew
            y -= pos * Pricer.skew_factor
            return y

        # get raw skewed prices based on position
        bid, ask = px(Side.BID), px(Side.ASK)

        # redistribute skew s.t.:
        # - you prices do not cross mid; and
        # - the spread for that bucket is maintained
        if ask < Pricer.min_half_spread:
            ask = Pricer.min_half_spread
            bid = - 2* half_spread + Pricer.min_half_spread
        if bid > - Pricer.min_half_spread:
            bid = - Pricer.min_half_spread
            ask = + 2* half_spread - Pricer.min_half_spread
        return bid, ask


class PriceLadder:

    def __init__(self):
        self.pricer = Pricer()
        self.fig, self.ax = plt.subplots()
        self.frames = []
        self._init_plot(self.fig, self.ax)
        # create df with zeros
        feature_list = ["Bucket", "half_spread", "bid_px", "ask_px"]
        self.df = pd.DataFrame(0, index=np.arange(len(self.pricer.buckets)), columns=feature_list)
        self.df["Bucket"] = self.pricer.buckets
        self._calc_ladder(0)
        self.df["half_spread"] = (self.df["ask_px"] - self.df["bid_px"]) / 2.0
        pass

    def set_position(self, pos: float):
        self._calc_ladder(pos)
        self._add_plot()
        pass

    def plot_baseline(self):
        plt.clf()
        # make plot with zero position
        self._calc_ladder(0)
        fig, ax = plt.subplots()
        self._init_plot(fig, ax)
        # add ticks
        xicks = self.df["Bucket"]
        ax.xaxis.set_ticks(xicks, "")
        # add legends
        bucket = 7
        x, y1, y2 = self.df["Bucket"].iloc[bucket], self.df["bid_px"].iloc[bucket], self.df["ask_px"].iloc[bucket]
        print(y1)
        # head_width=0.05, head_length=0.03, linewidth=1,
        dy = y2-y1
        ax.arrow(x=x, y=y1, dx=0, dy=dy,
                 head_width=5 * dy, head_length=0.5 * dy,
                 linewidth=8, length_includes_head=True,
                 color='green')
        #patch = patches.FancyArrowPatch((x, y1), (x, y2), arrowstyle='<|-|>', color='green', mutation_scale=1)
        #ax.add_patch(patch)
        ax.annotate(text='Spread', xy=(x, 0), xytext=(x + 1, y2 + 2 * dy), arrowprops=dict(facecolor='black', shrink=0.05))
        bucket = 1
        x, y1, y2 = self.df["Bucket"].iloc[bucket], self.df["bid_px"].iloc[bucket], self.df["ask_px"].iloc[bucket]
        dy = y2-y1
        ax.annotate(text='Retail', xy=(x, y2), xytext=(x - 2, y2 + 2 * dy), arrowprops=dict(facecolor='black', shrink=0.05))
        pix = self._plot_impl(self.df, ax)
        # save
        fig.savefig('statc.png', transparent=True)
        plt.close()

    @staticmethod
    def _init_plot(fig, ax):
        # shift x-axis to middle. clean other axis
        ax.spines['bottom'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        # Remove ticks, add labels
        ax.xaxis.set_ticks([]), ax.set_xlabel("Bucket", loc='right')
        # plt.yticks([]), ax.set_ylabel('Price', loc='top')
        ax.yaxis.set_ticks([]), ax.set_ylabel('Mid', loc='center')

        # set plot size etc
        fig.tight_layout()
        fig.set_size_inches(12.0, 5.8, forward=True)
        fig.set_dpi(120)

    def _calc_ladder(self, pos: float) -> None:
        self.df["bid_px"], self.df["ask_px"] = zip(*self.df.apply(lambda x: self.pricer.calc(x["Bucket"], x["half_spread"], pos), axis=1))
        # TODO - check ladder integrity

    @staticmethod
    def _plot_impl(df, ax):
        # plot the lines in the same plot so we can save it for animation
        linewidth = 8
        x = df["Bucket"]
        pix = ax.plot(
            x, df["ask_px"], 'r',
            x, df["bid_px"], 'b',
            linewidth=linewidth, path_effects=[pe.Stroke(linewidth=linewidth+2, foreground='k'), pe.Normal()])
        return pix

    def _add_plot(self):
        # self._init_plot(self.fig, self.ax)
        pix = self._plot_impl(self.df, self.ax)
        self.frames.append(pix)


def main():
    print("Hello")
    ladder = PriceLadder()
    # ladder.plot_baseline()
    for theta in range(0, 20, 1):
        theta /= 10.0
        theta *= np.pi
        pos = 25 * np.sin(theta)
        ladder.set_position(pos)
    anim = animation.ArtistAnimation(fig=ladder.fig, artists=ladder.frames, interval=250)
    writer = animation.PillowWriter()
    anim.save(filename="pillow_example.gif", writer=writer, dpi=120, savefig_kwargs={"transparent": True})
    #writer = animation.FFMpegWriter()
    #anim.save(filename="pillow_example.mp4", writer=writer, savefig_kwargs={"transparent": True})
    #plt.show()


if __name__ == "__main__":
    main()
