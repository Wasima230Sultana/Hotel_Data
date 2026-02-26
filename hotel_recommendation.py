# hotel_recommendation.py
def recommend_hotels(df, location=None, budget=None, amenities=None, min_rating=0, top_n=3):
    filtered_df = df.copy()
    
    if location:
        filtered_df = filtered_df[filtered_df['Location'].str.contains(location, case=False, na=False)]
    
    if budget:
        low, high = budget
        filtered_df = filtered_df[(filtered_df['Price per Night (BDT)'] >= low) &
                                  (filtered_df['Price per Night (BDT)'] <= high)]
    
    if amenities:
        filtered_df['Amenities'] = filtered_df['Amenities'].fillna('')
        for amenity in amenities:
            filtered_df = filtered_df[filtered_df['Amenities'].str.contains(amenity, case=False)]
    
    filtered_df = filtered_df[filtered_df['User Rating'] >= min_rating]
    recommended = filtered_df.sort_values(by=['User Rating','Price per Night (BDT)'], ascending=[False, True])
    
    return recommended.head(top_n)[['Hotel Name','Location','Price per Night (BDT)','User Rating','Amenities']]
