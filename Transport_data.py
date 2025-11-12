import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



st.set_page_config(page_title="Production Analysis", layout="wide")
st.title("📦 Production Analysis Dashboard")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file, sep=",", on_bad_lines="skip")
            st.success("✅ File uploaded successfully!")
            
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            # Lấy danh sách sheet
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names

            # Hiển thị danh sách sheet để chọn
            selected_sheet = st.selectbox("📑 Select a sheet to load:", sheet_names)

            # Đọc sheet được chọn
            data = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            st.success(f"✅ Excel file loaded successfully! (Sheet: {selected_sheet})")
        

        # ==========================
        # TABLE 1: SHOW THE DATA SET
        # ==========================
        st.subheader("📋 Dataset Preview")

        #Filter to show raw data
        if st.checkbox("Show Raw Dataset"):
           st.dataframe(data, use_container_width=True)

        # Chuẩn hóa tên cột
        if "Ngày YC giao hàng" in data.columns:
            data.rename(columns={"Ngày YC giao hàng": "Date"}, inplace=True)

        if "Route" not in data.columns or "Kg" not in data.columns:
            st.error("❌ The file must contain 'Route' and 'Kg' columns.")
        else:
            kg_month_2 = data[["Date", "Route", "Kg"]].copy()
            kg_month_2["Date"] = pd.to_datetime(kg_month_2["Date"], errors="coerce", dayfirst=True)
            

            kg_month_2["Kg"] = (
                kg_month_2["Kg"]
                .astype(str)
                .str.replace(r"[^\d\.,]", "", regex=True)   # bỏ ký tự lạ
                .str.replace(",", "", regex=False)          # bỏ dấu phẩy ngăn cách nghìn
            )

            kg_month_2["Kg"] = pd.to_numeric(kg_month_2["Kg"], errors="coerce")

            kg_month_2.dropna(subset=["Date", "Kg"], inplace=True)

            # ==========================
            # BIỂU ĐỒ 1: Volume by Month
            # ==========================
            kg_month_2["Month"] = kg_month_2["Date"].dt.month
            kg_month_2["Year"] = kg_month_2["Date"].dt.year

            monthly_sum = kg_month_2.groupby(["Year", "Month"])["Kg"].sum().reset_index()
            monthly_sum["Month-Year"] = (
                monthly_sum["Month"].astype(str) + "-" + monthly_sum["Year"].astype(str)
            )

            st.subheader("📅 Volume by Month")
            fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
            
            ax.plot(monthly_sum["Month-Year"], monthly_sum["Kg"], color="blue", markerfacecolor="white", markeredgecolor="white", linewidth=1.2)
            ax.set_title("Volume By Month", fontsize=10, color='white')
            ax.set_xlabel("Month", fontsize=8, color='white')
            ax.set_ylabel("Kg", fontsize=8, color='white')
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            

            for label in ax.get_xticklabels():
                label.set_color("white")
            for label in ax.get_yticklabels():
                label.set_color("white")
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=False)



            # ==========================
            # BIỂU ĐỒ 2: Volume by Route
            # ==========================
            st.subheader("🚚 Volume by Route")
            route_sum = kg_month_2.groupby(["Route"])["Kg"].sum().reset_index()

            fig1, ax1 = plt.subplots(figsize=(6, 3), dpi=150)
            ax1.plot(route_sum["Route"], route_sum["Kg"], marker='o', color="teal")
            ax1.set_title("Volume by Route", fontsize=10, color='white')
            ax1.set_xlabel("Route", fontsize=8, color='white')
            ax1.set_ylabel("Kg", fontsize=8, color='white')
            ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            for label in ax1.get_xticklabels():
                label.set_color("white")
            for label in ax1.get_yticklabels():
                label.set_color("white")
            fig1.patch.set_alpha(0)
            ax1.patch.set_alpha(0)
            plt.tight_layout()
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig1, use_container_width=False)

            # ==========================
            # TABLE 2: SHOW THE DATA SET
            # ==========================
            st.subheader("📋 Volume of Route per Day")
            Daily_sum = (
                kg_month_2.groupby(["Route", kg_month_2["Date"].dt.date])["Kg"]
                .sum()
                .reset_index()
                .rename(columns={"Date": "DayMonthYear"})
            )

            # Khi hiển thị, định dạng lại ngày
            Daily_sum["DayMonthYear"] = pd.to_datetime(Daily_sum["DayMonthYear"]).dt.strftime("%d-%m-%Y")

            # Sắp xếp đúng theo thời gian
            Daily_sum = Daily_sum.sort_values(by="DayMonthYear", key=lambda x: pd.to_datetime(x, format="%d-%m-%Y"))

            st.dataframe(Daily_sum, use_container_width=True)

            

            # ==========================
            # BIỂU ĐỒ 3: Volume of Route per Month
            # ==========================
            st.subheader("📈 Volume of Route per Month")

            kg_month_2["YearMonth"] = pd.to_datetime(kg_month_2["Date"]).dt.to_period("M").astype(str)
            monthly_sum = (
                kg_month_2.groupby(["Route", "YearMonth"])["Kg"].sum().reset_index()
            )

            fig2, ax2 = plt.subplots(figsize=(6, 3), dpi=150)
            for route in monthly_sum["Route"].unique():
                data_r = monthly_sum[monthly_sum["Route"] == route]
                ax2.plot(data_r["YearMonth"], data_r["Kg"], marker='o', label=route)
            ax2.set_title("Volume of Each Route per Month", fontsize=10, color='white')
            ax2.set_xlabel("Month", fontsize=8, color='white')
            ax2.set_ylabel("Kg", fontsize=8, color='white')
            ax2.legend(title="Route", bbox_to_anchor=(1.05, 1), loc="upper left")
            ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            for label in ax2.get_xticklabels():
                label.set_color("white")
            for label in ax2.get_yticklabels():
                label.set_color("white")
            fig2.patch.set_alpha(0)
            ax2.patch.set_alpha(0)
            plt.tight_layout()
            st.pyplot(fig2, use_container_width=False)

            # ==========================
            # BIỂU ĐỒ 4: Subplots nhỏ cho từng Route
            # ==========================
            st.subheader("📊 Volume by Route ")
            routes = monthly_sum["Route"].unique()
            n_routes = len(routes)
            ncols = 3
            nrows = (n_routes + ncols - 1) // ncols

            fig3, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 4*nrows))
            axes = axes.flatten()

            for i, route in enumerate(routes):
                data = monthly_sum[monthly_sum["Route"] == route]
                axes[i].plot(data["YearMonth"], data["Kg"], marker='o', color='steelblue')
                axes[i].set_title(f"Route: {route}")
                axes[i].set_xlabel("Month")
                axes[i].set_ylabel("Kg")
                axes[i].tick_params(axis='x', rotation=45)
                axes[i].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))



            # Ẩn các subplot trống nếu có
            for j in range(i+1, len(axes)):
                axes[j].set_visible(False)

    

            plt.tight_layout()
            plt.subplots_adjust(hspace=0.4, wspace=0.3)
            st.pyplot(fig3, use_container_width=False)

            # ==========================
            # END OF REPORT
            # ==========================
            st.subheader("END OF REPORT")
            

    except Exception as e:
        st.error(f"⚠️ Error while processing the file: {e}")
else:
    st.info("👆 Please upload a CSV file to start the analysis.")
