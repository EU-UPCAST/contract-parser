import unittest
from rdflib import Graph, URIRef
from contract_parser import ContractParser
import datetime

class TestContractParser(unittest.TestCase):

    def setUp(self):
        self.parser = ContractParser()
        self.test_file_path = "ComplianceAgreement.ttl"
        self.parser.load(self.test_file_path)

    @unittest.skip
    def test_load(self):
        self.assertIsInstance(self.parser.contract_graph, Graph)
        self.assertTrue(len(self.parser.contract_graph) > 0)

    def test_get_contract_uri(self):
        contract_uri = self.parser.get_contract_uri()
        self.assertIsInstance(contract_uri, URIRef)
        self.assertEqual(str(contract_uri), "http://upcast-project.eu/offer/example-contract")

    def test_get_provider(self):
        provider = self.parser.get_provider()
        self.assertIsInstance(provider, URIRef)
        self.assertEqual(str(provider), "https://upcast-project.eu/provider/example-data-provider")

    def test_get_consumer(self):
        consumer = self.parser.get_consumer()
        self.assertIsInstance(consumer, URIRef)
        self.assertEqual(str(consumer), "https://upcast-project.eu/consumer/example-data-consumer")

    def test_get_permitted_actions(self):
        permitted_actions = self.parser.get_permitted_actions()
        #permitted_actions_values = {action[1] for action in permitted_actions}
        self.assertEqual(permitted_actions, {"http://www.w3.org/ns/odrl/anonymize", "http://www.w3.org/ns/odrl/aggregate", "https://www.upcast-project.eu/upcast-vocab/1.0/Integrate","http://upcast-project.eu/dpws/example-dpw"})   

    def test_get_prohibited_actions(self):
        prohibited_actions = self.parser.get_prohibited_actions()
        #prohibited_actions_values = {action[1] for action in prohibited_actions}
        self.assertEqual(prohibited_actions, {"http://www.w3.org/ns/odrl/delete"})   


    def test_get_action_container(self):
        action_container = self.parser.get_action_container(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertEqual(action_container, "https://hub.docker.com/r/MyAnonymizer")     

    def test_get_action_execution_limits_single(self):
        action_execution_limit = self.parser.get_action_execution_limits(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertEqual(len(action_execution_limit),1)
        self.assertIn(("gteq",1), action_execution_limit)

        
    def test_get_action_execution_limits_double(self):
        action_execution_limit = self.parser.get_action_execution_limits(actionValue="http://www.w3.org/ns/odrl/aggregate")
        self.assertEqual(len(action_execution_limit),2)
        self.assertIn(("lteq",3), action_execution_limit)
        self.assertIn(("gteq",1), action_execution_limit)    


    def test_get_action_execution_limits_inexistent(self):
        action_execution_limit = self.parser.get_action_execution_limits(actionValue="https://www.upcast-project.eu/upcast-vocab/1.0/Integrate")
        self.assertEqual(len(action_execution_limit),0)

    def test_get_action_datetime_constraint_inexistent(self):
        action_datetime_constraints = self.parser.get_action_datetime_constraints(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertEqual(len(action_datetime_constraints),0)
    
    def test_get_action_datetime_constraint_single(self):
        action_datetime_constraints = self.parser.get_action_datetime_constraints(actionValue="http://www.w3.org/ns/odrl/aggregate")
        self.assertEqual(len(action_datetime_constraints),1)
        self.assertIn(("permission","lt",datetime.datetime(2025,5,30)), action_datetime_constraints)
            

    def test_get_action_datetime_constraint_double(self):
        action_datetime_constraints = self.parser.get_action_datetime_constraints(actionValue="https://www.upcast-project.eu/upcast-vocab/1.0/Integrate")
        self.assertEqual(len(action_datetime_constraints),2)
        self.assertIn(("permission","lt",datetime.datetime(2025,5,15)), action_datetime_constraints)
        self.assertIn(("permission","gt",datetime.datetime(2025,5,1)), action_datetime_constraints)    

    def test_get_action_energy_consumption_limit(self):
        action_energy_limit = self.parser.get_action_energy_consumption_limit(actionValue="https://www.upcast-project.eu/upcast-vocab/1.0/Integrate")
        self.assertEqual(action_energy_limit[0], 100)
        self.assertEqual(action_energy_limit[1], "http://qudt.org/vocab/unit#KilowattHour")


    def test_get_action_carbon_emission_limit(self):
        action_carbon_limit = self.parser.get_action_carbon_emission_limit(actionValue="http://www.w3.org/ns/odrl/aggregate")
        self.assertEqual(action_carbon_limit[0],200)
        self.assertEqual(action_carbon_limit[1], "http://qudt.org/vocab/unit#Kilogram")


    def test_get_action_carbon_emission_limit_inexistent(self):
        action_carbon_limit = self.parser.get_action_carbon_emission_limit(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertIsNone(action_carbon_limit)

        
    def test_get_action_energy_consumption_limit_inexistent(self):
        action_energy_limit = self.parser.get_action_energy_consumption_limit(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertIsNone(action_energy_limit)
        
    
    def test_get_action_dependencies(self):
        #action_dependencies = self.parser.get_action_dependencies(actionValue="http://www.w3.org/ns/odrl/anonymize")
        #self.assertEqual(["https://www.upcast-project.eu/upcast-vocab/1.0/Integrate"],action_dependencies)
        action_dependencies = self.parser.get_action_dependencies(actionValue="http://www.w3.org/ns/odrl/aggregate")
        self.assertEqual(["http://www.w3.org/ns/odrl/anonymize"],action_dependencies)

    def test_get_action_no_dependencies(self):
        action_dependencies = self.parser.get_action_dependencies(actionValue="https://www.upcast-project.eu/upcast-vocab/1.0/Integrate")
        self.assertEqual([],action_dependencies)

    @unittest.skip
    def test_query(self):
        query_string = """
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o .
        }
        LIMIT 10
        """
        results = self.parser.query(query_string)
        self.assertIsNotNone(results)

if __name__ == '__main__':
    unittest.main()