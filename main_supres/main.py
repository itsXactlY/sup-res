import os
import time
from dataclasses import dataclass
import pandas as pd
import pandas_ta.momentum as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import historical_data


@dataclass
class Values:
    ticker_csv: str
    selected_timeframe: str

    def __post_init__(self):
        self.ticker_csv = self.ticker_csv.upper()
        self.selected_timeframe = self.selected_timeframe.lower()


class Supres(Values):
    @staticmethod
    def main(ticker_csv, selected_timeframe, candle_count=254):
        print(f"Start main function in {time.perf_counter() - perf} seconds\n"
              f"{ticker_csv} data analysis in progress.")
        now_supres = time.perf_counter()
        df = pd.read_csv(ticker_csv, delimiter=',', encoding="utf-8-sig", index_col=False, nrows=candle_count,
                         keep_default_na=False)
        df = df.iloc[::-1]
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        df = pd.concat([df, df.tail(1)], axis=0, ignore_index=True)
        df.dropna(inplace=True)
        historical_hightimeframe = (historical_data.Client.KLINE_INTERVAL_1DAY,
                                    historical_data.Client.KLINE_INTERVAL_3DAY)
        historical_lowtimeframe = (historical_data.Client.KLINE_INTERVAL_1MINUTE,
                                   historical_data.Client.KLINE_INTERVAL_3MINUTE,
                                   historical_data.Client.KLINE_INTERVAL_5MINUTE,
                                   historical_data.Client.KLINE_INTERVAL_15MINUTE,
                                   historical_data.Client.KLINE_INTERVAL_30MINUTE,
                                   historical_data.Client.KLINE_INTERVAL_1HOUR,
                                   historical_data.Client.KLINE_INTERVAL_2HOUR,
                                   historical_data.Client.KLINE_INTERVAL_4HOUR,
                                   historical_data.Client.KLINE_INTERVAL_6HOUR,
                                   historical_data.Client.KLINE_INTERVAL_8HOUR,
                                   historical_data.Client.KLINE_INTERVAL_12HOUR)

        # Sma, Rsi, Macd, Fibonacci variables
        def indicators(ma_length1, ma_length2, ma_length3) -> tuple[tuple, tuple, tuple, tuple]:
            """
            Takes in three integer arguments, and returns a dataframe with three columns,
            each containing the moving average of the closing price for the given length.
            """
            dfsma = df[:-1]
            sma_1 = tuple((dfsma.ta.sma(ma_length1)))
            sma_2 = tuple((dfsma.ta.sma(ma_length2)))
            sma_3 = tuple((dfsma.ta.sma(ma_length3)))
            rsi_tuple = tuple((ta.rsi(df['close'][:-1])))
            return sma_1, sma_2, sma_3, rsi_tuple

        sma_values = 20, 50, 100
        sma1, sma2, sma3, rsi = indicators(*sma_values)
        support_list, resistance_list, fibonacci_uptrend, fibonacci_downtrend, pattern_list = [], [], [], [], []
        support_above, support_below, resistance_below, resistance_above, x_date = [], [], [], [], ''
        fibonacci_multipliers = 0.236, 0.382, 0.500, 0.618, 0.705, 0.786, 0.886
        # Chart settings
        legend_color, chart_color, background_color, support_line_color, resistance_line_color = \
            "#D8D8D8", "#E7E7E7", "#E7E7E7", "LightSeaGreen", "MediumPurple"
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0, row_width=[0.1, 0.1, 0.8])

        def support(candle_value, candle_index, before_candle_count, after_candle_count) -> (bool | None):
            """
            If the price of the asset is increasing for the last before_candle_count and decreasing for
            the last after_candle_count, then return True. Otherwise, return False.
            """
            try:
                for current_value in range(candle_index - before_candle_count + 1, candle_index + 1):
                    if candle_value.low[current_value] > candle_value.low[current_value - 1]:
                        return False
                for current_value in range(candle_index + 1, candle_index + after_candle_count + 1):
                    if candle_value.low[current_value] < candle_value.low[current_value - 1]:
                        return False
                return True
            except KeyError:
                pass

        def resistance(candle_value, candle_index, before_candle_count, after_candle_count) -> (bool | None):
            """
            If the price of the stock is increasing for the last before_candle_count and decreasing for the last
            after_candle_count, then return True. Otherwise, return False.
            """
            try:
                for current_value in range(candle_index - before_candle_count + 1, candle_index + 1):
                    if candle_value.high[current_value] < candle_value.high[current_value - 1]:
                        return False
                for current_value in range(candle_index + 1, candle_index + after_candle_count + 1):
                    if candle_value.high[current_value] > candle_value.high[current_value - 1]:
                        return False
                return True
            except KeyError:
                pass

        def fibonacci_pricelevels(high_price, low_price) -> tuple[list[float], list[float]]:
            """
            Uptrend Fibonacci Retracement Formula =>
            Fibonacci Price Level = High Price - (High Price - Low Price)*Fibonacci Level
            :param high_price: High price for the period
            :param low_price: Low price for the period
            """
            for multiplier in fibonacci_multipliers:
                retracement_levels_uptrend = low_price + (high_price - low_price) * multiplier
                fibonacci_uptrend.append(retracement_levels_uptrend)
                retracement_levels_downtrend = high_price - (high_price - low_price) * multiplier
                fibonacci_downtrend.append(retracement_levels_downtrend)
            return fibonacci_uptrend, fibonacci_downtrend

        def candlestick_patterns() -> list:
            """
            Takes in a dataframe and returns a list of candlestick patterns found in the dataframe then returns
            pattern list.
            """
            from candlestick import candlestick as cd
            nonlocal df
            all_patterns = [cd.inverted_hammer, cd.hammer, cd.doji, cd.bearish_harami, cd.bearish_engulfing,
                            cd.bullish_harami, cd.bullish_engulfing, cd.dark_cloud_cover, cd.dragonfly_doji,
                            cd.hanging_man, cd.gravestone_doji, cd.morning_star, cd.morning_star_doji,
                            cd.piercing_pattern, cd.star, cd.shooting_star]
            # Loop through the candlestick pattern functions
            for pattern in all_patterns:
                # Apply the candlestick pattern function to the data frame
                df = pattern(df)
            # Replace True values with 'pattern_found'
            df.replace({True: 'pattern_found'}, inplace=True)

            def pattern_find_func(pattern_row) -> list:
                """
                The function takes in a dataframe and a list of column names. It then iterates through the
                list of column names and checks if the column name is in the dataframe. If it is, it adds
                the column name to a list and adds the date of the match to another list.
                """
                t = 0
                pattern_find = [col for col in df.columns]
                for pattern_f in pattern_row:
                    if pattern_f == 'pattern_found':
                        pattern_list.append(
                            (pattern_find[t], pattern_row['date'].strftime('%b-%d-%y')))  # pattern, date
                    t += 1
                return pattern_list

            return df.iloc[-3:-30:-1].apply(pattern_find_func, axis=1)

        def sensitivity(sens=2) -> tuple[list, list]:
            """
            Find the support and resistance levels for a given asset.
            sensitivity:1 is recommended for daily charts or high frequency trade scalping.
            :param sens: sensitivity parameter default:2, level of detail 1-2-3 can be given to function
            """
            for sens_row in range(3, len(df) - 1):
                if support(df, sens_row, 3, sens):
                    support_list.append((sens_row, df.low[sens_row]))
                if resistance(df, sens_row, 3, sens):
                    resistance_list.append((sens_row, df.high[sens_row]))
            return support_list, resistance_list

        def chart_lines():
            """
            Check if the support and resistance lines are above or below the latest close price.
            """
            # Find support and resistance levels
            # Check if the support is below the latest close. If it is, it is appending it to the list
            # support_below. If it isn't, it is appending it to the list resistance_below.
            all_support_list = tuple(map(lambda sup1: sup1[1], support_list))
            all_resistance_list = tuple(map(lambda res1: res1[1], resistance_list))
            latest_close = df['close'].iloc[-1]
            for support_line in all_support_list:  # Find closes
                if support_line < latest_close:
                    support_below.append(support_line)
                else:
                    resistance_below.append(support_line)
            if len(support_below) == 0:
                support_below.append(min(df.low))
            # Check if the price is above the latest close price. If it is, it is appending it to the
            # resistance_above list. If it is not, it is appending it to the support_above list.
            for resistance_line in all_resistance_list:
                if resistance_line > latest_close:
                    resistance_above.append(resistance_line)
                else:
                    support_above.append(resistance_line)
            if len(resistance_above) == 0:
                resistance_above.append(max(df.high))
            lowest_support = min(support_below)
            highest_resistance = max(resistance_above)
            return fibonacci_pricelevels(highest_resistance, lowest_support)

        def legend_candle_patterns() -> None:
            """
            The function takes the list of candlestick patterns and adds them to the chart as a legend text.
            """
            fig.add_trace(go.Scatter(
                y=[support_list[0]], name="----------------------------------------", mode="markers",
                marker=dict(color=legend_color, size=14)))
            fig.add_trace(go.Scatter(
                y=[support_list[0]], name="Latest Candlestick Patterns", mode="markers",
                marker=dict(color=legend_color, size=14)))
            for pat1, count in enumerate(pattern_list):  # Candlestick patterns
                fig.add_trace(go.Scatter(
                    y=[support_list[0]], name=f"{pattern_list[pat1][1]} : {str(pattern_list[pat1][0]).capitalize()}",
                    mode="lines", marker=dict(color=legend_color, size=10)))

        def create_candlestick_plot() -> None:
            """
            Creates a candlestick plot using the dataframe df, and adds it to the figure.
            """
            fig.add_trace(go.Candlestick(x=df['date'][:-1].dt.strftime(x_date), name="Candlestick",
                                         text=df['date'].dt.strftime(x_date), open=df['open'], high=df['high'],
                                         low=df['low'], close=df['close']), row=1, col=1)

        def add_volume_subplot() -> None:
            """
            Adds a volume subplot to the figure.
            """
            fig.add_trace(go.Bar(x=df['date'][:-1].dt.strftime(x_date), y=df['Volume USDT'], name="Volume USDT",
                                 showlegend=False), row=2, col=1)

        def add_rsi_subplot() -> None:
            """
            Adds a subplot to the figure object called fig, which is a 3x1 grid of subplots. The
            subplot is a scatter plot of the RSI values, with a horizontal line at 30 and 70, and a gray
            rectangle between the two lines.
            """
            fig.add_trace(go.Scatter(x=df['date'][:-1].dt.strftime(x_date), y=rsi, name="RSI",
                                     showlegend=False), row=3, col=1)
            fig.add_hline(y=30, name="RSI lower band", line=dict(color='red', width=1), line_dash='dash', row=3, col=1)
            fig.add_hline(y=70, name="RSI higher band", line=dict(color='red', width=1), line_dash='dash', row=3, col=1)
            fig.add_hrect(y0=30, y1=70, line_width=0, fillcolor="gray", opacity=0.2, row=3, col=1)

        def draw_support() -> None:
            """
            Draws the support lines and adds annotations to the chart.
            """
            for s in range(len(support_list)):
                # Support lines
                fig.add_shape(type='line', x0=support_list[s][0] - 1, y0=support_list[s][1],
                              x1=len(df) + 25,
                              y1=support_list[s][1], line=dict(color=support_line_color, width=2))
                # Support annotations
                fig.add_annotation(x=len(df) + 7, y=support_list[s][1], text=str(support_list[s][1]),
                                   font=dict(size=15, color=support_line_color))

        def draw_resistance() -> None:
            """
            Draws the resistance lines and adds annotations to the chart.
            """
            for r in range(len(resistance_list)):
                # Resistance lines
                fig.add_shape(type='line', x0=resistance_list[r][0] - 1, y0=resistance_list[r][1],
                              x1=len(df) + 25,
                              y1=resistance_list[r][1], line=dict(color=resistance_line_color, width=1))
                # Resistance annotations
                fig.add_annotation(x=len(df) + 20, y=resistance_list[r][1], text=str(resistance_list[r][1]),
                                   font=dict(size=15, color=resistance_line_color))

        def legend_texts() -> None:
            """
            Adds a trace to the chart for each indicator, and then adds a trace for each indicator's value.
            """
            fig.add_trace(go.Scatter(
                y=[support_list[0]], name=f"Resistances    ||   Supports", mode="markers+lines",
                marker=dict(color=resistance_line_color, size=10)))
            sample_price = df['close'][0]
            str_price_len = len(str(sample_price)) if sample_price < 1 else 3

            def legend_support_resistance_values() -> None:
                """
                Takes the support and resistance values and adds them to the legend.
                """
                temp = 0
                blank = " " * (len(str(sample_price)) + 1)
                differ = abs(len(float_resistance_above) - len(float_support_below))
                try:
                    if len(float_resistance_above) < len(float_support_below):
                        float_resistance_above.extend([0] * differ)
                    else:
                        float_support_below.extend([0] * differ)
                    for _ in range(min(max(len(float_resistance_above), len(float_support_below)), 12)):
                        if float_resistance_above[temp] == 0:  # This is for legend alignment
                            legend_supres = f"{float(float_resistance_above[temp]):.{str_price_len - 1}f}{blank}     " \
                                            f"||   {float(float_support_below[temp]):.{str_price_len - 1}f}"
                        else:
                            legend_supres = f"{float(float_resistance_above[temp]):.{str_price_len - 1}f}       " \
                                            f"||   {float(float_support_below[temp]):.{str_price_len - 1}f}"
                        fig.add_trace(go.Scatter(y=[support_list[0]], name=legend_supres, mode="lines",
                                                 marker=dict(color=legend_color, size=10)))
                        temp += 1 if temp < 12 else 0
                except IndexError:
                    pass

            def text_and_indicators() -> None:
                """
                Adds a trace to the chart for each indicator, and then adds a trace for each indicator's value.
                """
                fig.add_trace(go.Scatter(
                    y=[support_list[0]], name=f"github.com/arabacibahadir/sup-res", mode="markers",
                    marker=dict(color=legend_color, size=0)))
                fig.add_trace(go.Scatter(
                    y=[support_list[0]], name=f"RSI          : {int(rsi[-1])}", mode="lines",
                    marker=dict(color=legend_color, size=10)))
                # Add SMA1, SMA2, and SMA3 to the chart and legend
                fig.add_trace(go.Scatter(x=df['date'].dt.strftime(x_date), y=sma1,
                                         name=f"SMA{sma_values[0]}     : {float(sma1[-1]):.{str_price_len}f}",
                                         line=dict(color='#5c6cff', width=3)))
                fig.add_trace(go.Scatter(x=df['date'].dt.strftime(x_date), y=sma2,
                                         name=f"SMA{sma_values[1]}     : {float(sma2[-1]):.{str_price_len}f}",
                                         line=dict(color='#950fba', width=3)))
                fig.add_trace(go.Scatter(x=df['date'].dt.strftime(x_date), y=sma3,
                                         name=f"SMA{sma_values[2]}   : {float(sma3[-1]):.{str_price_len}f}",
                                         line=dict(color='#a69b05', width=3)))
                fig.add_trace(go.Scatter(
                    y=[support_list[0]], name=f"       Fibonacci Uptrend | Downtrend ", mode="markers",
                    marker=dict(color=legend_color, size=0)))

            def legend_fibonacci() -> None:
                """
                Adds to the legend for each Fibonacci level text.
                """
                mtp = len(fibonacci_multipliers) - 1
                for _ in fibonacci_uptrend:
                    fig.add_trace(go.Scatter(
                        y=[support_list[0]],
                        name=f"Fib {fibonacci_multipliers[mtp]:.3f} "
                             f": {float(fibonacci_uptrend[mtp]):.{str_price_len}f} "
                             f"| {float(fibonacci_downtrend[mtp]):.{str_price_len}f} ",
                        mode="lines",
                        marker=dict(color=legend_color, size=10)))
                    mtp -= 1

            legend_support_resistance_values()
            text_and_indicators()
            legend_fibonacci()
            # Candle patterns for HTF
            if selected_timeframe in historical_hightimeframe:
                legend_candle_patterns()

        def chart_updates() -> None:
            """
            Updates the chart's layout, background color, chart color, legend color, and margin.
            """
            fig.update_layout(title=str(f"{historical_data.ticker} {selected_timeframe.upper()} Chart"),
                              hovermode='x', dragmode="zoom",
                              paper_bgcolor=background_color, plot_bgcolor=chart_color, xaxis_rangeslider_visible=False,
                              legend=dict(bgcolor=legend_color, font=dict(size=11)), margin=dict(t=30, l=0, b=0, r=0))
            fig.update_xaxes(showspikes=True, spikecolor="green", spikethickness=2)
            fig.update_yaxes(showspikes=True, spikecolor="green", spikethickness=2)

        def save():
            """
            Saves the image and html file of the plotly chart, then it tweets the image and text
            """
            if not os.path.exists("../main_supres/images"):
                os.mkdir("images")
            image = \
                f"../main_supres/images/{df['date'].dt.strftime('%b-%d-%y')[candle_count]}{historical_data.ticker}.jpeg"
            fig.write_image(image, width=1920, height=1080)  # Save image for tweet
            fig.write_html(
                f"../main_supres/images/"
                f"{df['date'].dt.strftime('%b-%d-%y')[candle_count]}{historical_data.ticker}.html",
                full_html=False, include_plotlyjs='cdn')
            text_image = f"#{historical_data.ticker} " \
                         f"{selected_timeframe} Support and resistance levels \n " \
                         f"{df['date'].dt.strftime('%b-%d-%Y')[candle_count]}"

            def send_tweet() -> None:
                """
                Takes a screenshot of a chart, then tweets it with a caption.
                """
                import tweet
                tweet.send_tweet(image, text_image)
                while tweet.is_image_tweet().text != text_image:
                    time.sleep(1)
                    if tweet.is_image_tweet().text != text_image:
                        resistance_above_nonzero = list(filter(lambda x: x != 0, float_resistance_above))
                        support_below_nonzero = list(filter(lambda x: x != 0, float_support_below))
                        tweet.api.update_status(status=f"#{historical_data.ticker}  "
                                                       f"{df['date'].dt.strftime('%b-%d-%Y')[candle_count]} "
                                                       f"{selected_timeframe} Support and resistance levels"
                                                       f"\nRes={resistance_above_nonzero[:7]} \n"
                                                       f"Sup={support_below_nonzero[:7]}",
                                                in_reply_to_status_id=tweet.is_image_tweet().id)
                    break
            # send_tweet()

        def pinescript_code() -> str:
            """
            Writes resistance and support lines to a file called pinescript.txt.
            """
            pinescript_lines = []
            lines_sma = f"//@version=5\nindicator('Sup-Res {historical_data.ticker} {selected_timeframe}'," \
                        f" overlay=true)\n" \
                        "plot(ta.sma(close, 50), title='50 SMA', color=color.new(color.blue, 0), linewidth=1)\n" \
                        "plot(ta.sma(close, 100), title='100 SMA', color=color.new(color.purple, 0), linewidth=1)\n" \
                        "plot(ta.sma(close, 200), title='200 SMA', color=color.new(color.red, 0), linewidth=1)\n"

            for line_res in float_resistance_above[:10]:
                if line_res == 0:
                    continue
                lr = f"hline({line_res}, title=\"Lines\", color=color.red, linestyle=hline.style_solid, linewidth=1)"
                pinescript_lines.append(lr)

            for line_sup in float_support_below[:10]:
                if line_sup == 0:
                    continue
                ls = f"hline({line_sup}, title=\"Lines\", color=color.green, linestyle=hline.style_solid, linewidth=1)"
                pinescript_lines.append(ls)
            lines = '\n'.join(map(str, pinescript_lines))
            # Create a new file that called pinescript.txt and write the lines_sma and lines variables to the file
            with open("../main_supres/pinescript.txt", "w") as pine:
                pine.writelines(lines_sma + lines)

                def ichimoku():  # read ichimoku_cloud.txt and write it to pinescript.txt
                    with open("pinescripts/ichimoku_cloud.txt", "r") as ichimoku_read:
                        # write a blank line to separate the ichimoku cloud from the support and resistance lines
                        pine.write("\n")
                        pine.writelines(ichimoku_read.read())

                def daily_levels():
                    with open("pinescripts/daily_levels.txt", "r") as d_levels:
                        pine.write("\n")
                        pine.writelines(d_levels.read())

                ichimoku()
                daily_levels()
            return lines

        sensitivity()
        chart_lines()
        # Checking if the selected timeframe is in the historical_hightimeframe list.
        if selected_timeframe in historical_hightimeframe:
            candlestick_patterns()
            x_date = '%b-%d-%y'
        elif selected_timeframe in historical_lowtimeframe:
            x_date = '%H:%M %d-%b'
        create_candlestick_plot()
        add_volume_subplot()
        add_rsi_subplot()
        float_resistance_above = list(map(float, sorted(resistance_above + resistance_below)))
        float_support_below = list(map(float, sorted(support_below + support_above, reverse=True)))
        draw_support()
        draw_resistance()
        legend_texts()
        chart_updates()
        # save()
        # pinescript_code()
        print(f"Completed sup-res execution in {time.perf_counter() - now_supres} seconds")
        print(f"Completed execution in total {time.perf_counter() - perf} seconds")
        return fig.show(id='the_graph', config={'displaylogo': False})


if __name__ == "__main__":
    os.chdir("../main_supres")  # Change the directory to the main_supres folder
    file_name = historical_data.user_ticker.file_name
    try:
        perf = time.perf_counter()
        historical_data.user_ticker.historical_data_write()
        if os.path.isfile(file_name):  # Check .csv file exists
            print(f"{file_name} downloaded and created.")
            Supres.main(file_name, historical_data.time_frame)
            print("Data analysis is done. Browser opening.")
            os.remove(file_name)  # remove the .csv file
            print(f"{file_name} file deleted.")
        else:
            raise print("One or more issues caused the download to fail. "
                        "Make sure you typed the filename correctly.")
    except KeyError:
        os.remove(file_name)
        raise KeyError("Key error, algorithm issue")
