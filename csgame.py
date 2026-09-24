# --- LIVE LEADERBOARD DISPLAY ---
st.markdown("---")
st.subheader("🏆 Live Leaderboard")

try:
    # Fetch data records directly from the Google Sheets worksheet
    sheet = init_google_sheet()
    records = sheet.get_all_records()
    
    if records:
        # Convert dictionary records into a Pandas DataFrame
        df = pd.DataFrame(records)
        
        # 1. Ensure 'Duration (seconds)' is numeric for proper sorting
        df['Duration (seconds)'] = pd.to_numeric(df['Duration (seconds)'], errors='coerce')
        
        # 2. Sort by fastest completion time (ascending)
        df = df.sort_values(by='Duration (seconds)', ascending=True).reset_index(drop=True)
        
        # 3. Add custom Rank icons for top players
        def format_rank(index):
            if index == 0:
                return "🥇 1st"
            elif index == 1:
                return "🥈 2nd"
            elif index == 2:
                return "🥉 3rd"
            else:
                return f"{index + 1}th"

        df.insert(0, 'Rank', [format_rank(i) for i in range(len(df))])
        
        # 4. Display formatted table without the raw index
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No scores submitted yet.")

except Exception as e:
    st.caption("Leaderboard loading...")
