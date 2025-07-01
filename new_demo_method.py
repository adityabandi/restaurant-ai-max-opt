    def _load_demo_data(self):
        """Load comprehensive demo data for testing including multiple data types"""
        # Create realistic sales demo data
        sales_data = [
            {'item_name': 'Classic Burger', 'quantity': 45, 'price': 16.99, 'total_amount': 764.55},
            {'item_name': 'Caesar Salad', 'quantity': 12, 'price': 14.99, 'total_amount': 179.88},
            {'item_name': 'Margherita Pizza', 'quantity': 28, 'price': 18.99, 'total_amount': 531.72},
            {'item_name': 'Grilled Salmon', 'quantity': 22, 'price': 24.99, 'total_amount': 549.78},
            {'item_name': 'Chicken Wings', 'quantity': 35, 'price': 12.99, 'total_amount': 454.65},
            {'item_name': 'Fish Tacos', 'quantity': 19, 'price': 15.99, 'total_amount': 303.81},
            {'item_name': 'Craft Beer', 'quantity': 67, 'price': 6.99, 'total_amount': 468.33},
            {'item_name': 'House Wine', 'quantity': 31, 'price': 8.99, 'total_amount': 278.69},
            {'item_name': 'Chocolate Cake', 'quantity': 15, 'price': 7.99, 'total_amount': 119.85},
            {'item_name': 'Truffle Pasta', 'quantity': 8, 'price': 26.99, 'total_amount': 215.92}
        ]
        
        # Create matching inventory data
        inventory_data = [
            {'item_name': 'Classic Burger', 'quantity': 53, 'unit_cost': 5.75, 'category': 'Entrees'},
            {'item_name': 'Caesar Salad', 'quantity': 7, 'unit_cost': 4.25, 'category': 'Salads'},
            {'item_name': 'Margherita Pizza', 'quantity': 42, 'unit_cost': 6.50, 'category': 'Pizza'},
            {'item_name': 'Grilled Salmon', 'quantity': 18, 'unit_cost': 9.95, 'category': 'Entrees'},
            {'item_name': 'Chicken Wings', 'quantity': 105, 'unit_cost': 4.80, 'category': 'Appetizers'},
            {'item_name': 'Fish Tacos', 'quantity': 5, 'unit_cost': 5.25, 'category': 'Entrees'},
            {'item_name': 'Craft Beer', 'quantity': 150, 'unit_cost': 2.10, 'category': 'Beverages'},
            {'item_name': 'House Wine', 'quantity': 42, 'unit_cost': 3.50, 'category': 'Beverages'},
            {'item_name': 'Chocolate Cake', 'quantity': 20, 'unit_cost': 2.75, 'category': 'Desserts'},
            {'item_name': 'Truffle Pasta', 'quantity': 16, 'unit_cost': 9.80, 'category': 'Pasta'}
        ]
        
        # Store in session state with multiple datasets
        st.session_state.uploaded_data = {
            'upload_id': 'demo-multi',
            'filenames': ['demo_sales.csv', 'demo_inventory.csv'],
            'data_types': ['sales', 'inventory'],
            'processed_data': sales_data + inventory_data,  # Combined for backward compatibility
            'individual_datasets': [sales_data, inventory_data],
            'ai_confidence': 0.95
        }
        
        # Set cross-file analysis flag
        st.session_state.cross_file_analysis = True
        
        # Generate insights from all data
        self._generate_insights_from_multiple_sources([sales_data, inventory_data], ['sales', 'inventory'])
        
        st.success("🎉 Demo data loaded! Explore restaurant analytics with cross-dataset analysis.")
        st.rerun()
