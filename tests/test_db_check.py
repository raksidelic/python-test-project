import allure

@allure.feature("Infrastructure Checks")
class TestInfrastructure:

    @allure.story("PostgreSQL Connection and Data Check")
    def test_postgresql_connection(self, sql_client):
        """
        This test:
        1. Connects to DB using sql_client fixture.
        2. Queries the 'users' table.
        3. Verifies the existence of the 'onur_admin' user.
        """
        
        with allure.step("Executing SELECT query on database"):
            # sql_client is a powerful object coming from conftest.py utilizing Config
            rows = sql_client.execute_query("SELECT username, role FROM users WHERE username = 'onur_admin'")
        
        with allure.step("Verifying results"):
            assert rows is not None, "Database connection failed or query did not run!"
            assert len(rows) > 0, "Query returned empty! Was seeding performed?"
            
            user_data = rows[0]
            username = user_data[0]
            role = user_data[1]
            
            print(f"\n[DB SUCCESS] User Found: {username} | Role: {role}")
            
            assert username == "onur_admin"
            assert role == "admin"