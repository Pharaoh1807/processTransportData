import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



st.set_page_config(page_title="Production Analysis", layout="wide")
st.title("📦 Production Analysis Dashboard")

uploaded_file = st.file_uploader("📂 Upload your data file", type=["csv", "xlsx", "xls"])

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

        # ==========================
        # CHỌN CHẾ ĐỘ PHÂN TÍCH
        # ==========================
        st.subheader("Chọn chế độ phân tích")
        mode = st.radio(
            "Vui lòng chọn một mục:",
            ["Production Analytic", "Total Cost Analytic"],
            horizontal=True
        )

        # ==========================
        # CHUẨN HÓA DỮ LIỆU CHUNG
        # ==========================

        if "Ngày YC giao hàng" in data.columns:
            data.rename(columns={"Ngày YC giao hàng": "Date"}, inplace=True)

        if "Route" not in data.columns or "Kg" not in data.columns:
            st.error("❌ The file must contain 'Route' and 'Kg' columns.")
        else:
            kg_month = data[["Date", "Route", "Kg"]].copy()
            kg_month["Date"] = pd.to_datetime(kg_month["Date"], errors="coerce", dayfirst=True)
            
            # làm sạch số liệu cột Kg
            kg_month["Kg"] = (
                kg_month["Kg"]
                .astype(str)
                .str.replace(r"[^\d\.,]", "", regex=True)   # bỏ ký tự lạ
                .str.replace(",", "", regex=False)          # bỏ dấu phẩy ngăn cách nghìn
            )

            kg_month["Kg"] = pd.to_numeric(kg_month["Kg"], errors="coerce")

            kg_month.dropna(subset=["Date", "Kg"], inplace=True)

        # ==========================
        # MODE 1 : PHÂN TÍCH SẢN LƯỢNG
        # ==========================
        if mode == "Production Analytic":
            st.header("📊 Production Analysis Report")

            # ==========================
            # BIỂU ĐỒ 1: Volume by Month
            # ==========================
            kg_month["Month"] = kg_month["Date"].dt.month
            kg_month["Year"] = kg_month["Date"].dt.year

            monthly_sum = kg_month.groupby(["Year", "Month"])["Kg"].sum().reset_index()
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
            route_sum = kg_month.groupby(["Route"])["Kg"].sum().reset_index()

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
            # TABLE 2: SHOW THE DATA SET - Volume of Route per Day
            # ==========================
            st.subheader("📋 Volume of Route per Day")
            Daily_sum = (
                kg_month.groupby(["Route", kg_month["Date"].dt.date])["Kg"]
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

            kg_month["YearMonth"] = pd.to_datetime(kg_month["Date"]).dt.to_period("M").astype(str)
            monthly_sum = (
                kg_month.groupby(["Route", "YearMonth"])["Kg"].sum().reset_index()
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

        else:
            # ==========================
            # MODE 2 : TOTAL COST ANALYTIC
            # ==========================
            if mode == "Total Cost Analytic":

                st.header("Total Cost Analysis Report")

                # ============================================================
                # KHỞI TẠO DANH SÁCH BẢNG GIÁ CHO NHIỀU NHÀ VẬN CHUYỂN (NVC)
                # ============================================================
                if "all_price_tables" not in st.session_state:
                    st.session_state["all_price_tables"] = []   # list = [{name, df}]
                if "ready_to_compare" not in st.session_state:
                    st.session_state["ready_to_compare"] = False
                
                price_file = st.file_uploader("📂 Upload ONE price file", 
                                            type=["xlsx", "xls", "csv"], 
                                            key="price_upload")
                
                
                # ============================================================
                # UPLOAD 1 FILE GIÁ + LƯU TÊN NVC
                # ============================================================
                


                if price_file:
                    supplier_name = st.text_input("✏️ Supplier name", value=price_file.name.split(".")[0])

                    if st.button("➕ Add this price file"):
                        try:
                            # Load file
                            if price_file.name.endswith(".csv"):
                                price_df = pd.read_csv(price_file)
                            else:
                                xls = pd.ExcelFile(price_file)
                                sheet = st.selectbox("📑 Select sheet", xls.sheet_names)
                                price_df = pd.read_excel(price_file, sheet_name=sheet)

                            # Store in session
                            st.session_state["all_price_tables"].append(
                                {"name": supplier_name, "df": price_df}
                            )

                            st.success(f"✅ Added price for : **{supplier_name}**")
                            if st.checkbox("Show Production data with OTKX"):
                                st.dataframe(price_df, use_container_width=True)

                        except Exception as e:
                            st.error(f"⚠️ Error: {e}")

                # ============================================================
                # SHOW ALL PRICE TABLES ALREADY LOADED
                # ============================================================
                if st.session_state["all_price_tables"]:
                    st.info("You can upload more files or click the button below to start comparing.")

                    if st.button("Finish Upload — Compare All Suppliers"):
                        st.session_state["ready_to_compare"] = True

                if st.session_state["ready_to_compare"]:
                    if st.checkbox("Show All Uploaded Price Tables"):    
                        for p in st.session_state["all_price_tables"]:
                            st.write(f"### 🚚 Supplier: {p['name']}")
                            st.dataframe(p["df"], use_container_width=True)

                    # ============================================================
                    # XÁC ĐỊNH KHUNG TẢI OTKX
                    # ============================================================
                    def get_otkx(kg):
                        if kg <= 1000: return "OTKX01"
                        elif kg <= 2500: return "OTKX03"
                        elif kg <= 5000: return "OTKX05"
                        elif kg <= 10000: return "OTKX10"
                        elif kg <= 15000: return "OTKX15"
                        elif kg <= 20000: return "OTKX20"
                        else: return "OTKX45"

                    kg_month["OTKX"] = kg_month["Kg"].apply(get_otkx)
                    if st.checkbox("Show Production data with OTKX"):
                        st.subheader("📦 Production data with OTKX")
                        st.dataframe(kg_month, use_container_width=True)

                    # ============================================================
                    # TÍNH CHI PHÍ CHO TỪNG NVC
                    # ============================================================
                    if st.session_state["all_price_tables"]:

                        st.header("📊 Cost Comparison for All Transporters")

                        final_results = []

                        for p in st.session_state["all_price_tables"]:
                            supplier_name = p["name"]
                            price_df = p["df"]

                            if "TUYẾN" not in price_df.columns:
                                st.error(f"❌ Price file of {supplier_name} missing column 'TUYẾN'")
                                continue

                            merged = pd.merge(
                                kg_month,
                                price_df,
                                left_on="Route",
                                right_on="TUYẾN",
                                how="left"
                            )

                            # lấy giá theo khung tải OTKX
                            merged["UnitPrice"] = merged.apply(
                                lambda row: row.get(row["OTKX"], None),
                                axis=1
                            )

                            merged["TotalCost"] = merged["Kg"] * merged["UnitPrice"] / 1000
                            total_cost = merged["TotalCost"].sum()

                            # Lưu kết quả
                            final_results.append({
                                "Supplier": supplier_name,
                                "TotalCost": total_cost,
                                "Detail": merged
                            })

                        # ============================================================
                        # BẢNG SO SÁNH CHI PHÍ
                        # ============================================================
                        compare_df = pd.DataFrame([
                            {"Supplier": r["Supplier"], "Total Cost (VND)": int(r["TotalCost"])}
                            for r in final_results
                        ])


                        st.subheader("📊 Total Cost Comparison")
                        df_style = compare_df.style.format({
                            "Total Cost (VND)": "{:,.0f}"   # định dạng có dấu phẩy
                        })

                        st.dataframe(df_style, use_container_width=False)
                       

                        # BAR CHART TOTAL COST
                        

                        fig, ax = plt.subplots(figsize=(4, 2.5), dpi=150)
                        df = compare_df.set_index("Supplier")
                        ax.bar(df.index, df["Total Cost (VND)"], color="#ff8c00", width=0.2)  # orange
                        ax.set_xticks(range(len(df.index)))
                        ax.set_title("Total Cost Comparison", fontsize=10, color='white')
                        ax.set_xticklabels(df.index, rotation=30, ha='right')
                        # Format trục Y bằng dấu phẩy
                        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
                        for spine in ax.spines.values():
                            spine.set_visible(False)

                        fig.patch.set_alpha(0)       
                        ax.patch.set_alpha(0)
                        #ax.set_xlabel("Supplier", fontsize=8, color='white')
                        #ax.set_ylabel("Total Cosr", fontsize=8, color='white')
                        for label in ax.get_xticklabels():
                            label.set_color("white")
                            label.set_fontsize(6)
                        for label in ax.get_yticklabels():
                            label.set_color("white")
                            label.set_fontsize(6)       

                        
                        plt.tight_layout()
                        st.pyplot(fig, use_container_width=False)

                        # ============================================================
                        # SHOW DETAIL EACH Supplier
                        # ============================================================
                        st.subheader("📚 Detailed Merged Data")
                        if st.checkbox("Show Merged Details for Each supplier"):
                            for r in final_results:
                                st.write(f"### 🚚 {r['Supplier']}")
                                st.dataframe(
                                    r["Detail"][["Date", "Route", "Kg", "OTKX", "UnitPrice", "TotalCost"]],
                                    use_container_width=False
                                )
                        

    except Exception as e:
        st.error(f"⚠️ Error while processing the file: {e}")
else:
    st.info("👆 Please upload a CSV file to start the analysis.")


        