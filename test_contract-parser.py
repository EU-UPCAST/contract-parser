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
        self.assertEquals(str(contract_uri), "http://upcast-project.eu/offer/example-contract")

    def test_get_provider(self):
        provider = self.parser.get_provider()
        self.assertIsInstance(provider, URIRef)
        self.assertEquals(str(provider), "https://upcast-project.eu/provider/example-data-provider")

    def test_get_consumer(self):
        consumer = self.parser.get_consumer()
        self.assertIsInstance(consumer, URIRef)
        self.assertEquals(str(consumer), "https://upcast-project.eu/consumer/example-data-consumer")

    def test_get_permitted_actions(self):
        permitted_actions = self.parser.get_permitted_actions()
        permitted_actions_values = {action[1] for action in permitted_actions}
        self.assertEquals(permitted_actions_values, {"http://www.w3.org/ns/odrl/anonymize", "http://www.w3.org/ns/odrl/aggregate", "https://www.upcast-project.eu/upcast-vocab/1.0/Integrate"})   

    def test_get_action_container(self):
        action_container = self.parser.get_action_container(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertEquals(action_container, "https://hub.docker.com/r/MyAnonymizer")     

    def test_get_action_execution_limits_single(self):
        action_execution_limit = self.parser.get_action_execution_limits(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertEquals(len(action_execution_limit),1)
        self.assertIn(("gteq",1), action_execution_limit)

        
    def test_get_action_execution_limits_double(self):
        action_execution_limit = self.parser.get_action_execution_limits(actionValue="http://www.w3.org/ns/odrl/aggregate")
        self.assertEquals(len(action_execution_limit),2)
        self.assertIn(("lteq",3), action_execution_limit)
        self.assertIn(("gteq",1), action_execution_limit)    


    def test_get_action_execution_limits_inexistent(self):
        action_execution_limit = self.parser.get_action_execution_limits(actionValue="https://www.upcast-project.eu/upcast-vocab/1.0/Integrate")
        self.assertEquals(len(action_execution_limit),0)

    def test_get_action_datetime_constraint_inexistent(self):
        action_datetime_constraints = self.parser.get_action_datetime_constraints(actionValue="http://www.w3.org/ns/odrl/anonymize")
        self.assertEquals(len(action_datetime_constraints),0)
    
    def test_get_action_datetime_constraint_single(self):
        action_datetime_constraints = self.parser.get_action_datetime_constraints(actionValue="http://www.w3.org/ns/odrl/aggregate")
        self.assertEquals(len(action_datetime_constraints),1)
        self.assertIn(("lt",datetime.datetime(2025,5,30)), action_datetime_constraints)
            

    def test_get_action_datetime_constraint_double(self):
        action_datetime_constraints = self.parser.get_action_datetime_constraints(actionValue="https://www.upcast-project.eu/upcast-vocab/1.0/Integrate")
        self.assertEquals(len(action_datetime_constraints),2)
        self.assertIn(("lt",datetime.datetime(2025,5,15)), action_datetime_constraints)
        self.assertIn(("gt",datetime.datetime(2025,5,1)), action_datetime_constraints)    
    
    def test_get_action_dependencies(self):
        #action_dependencies = self.parser.get_action_dependencies(actionValue="http://www.w3.org/ns/odrl/anonymize")
        #self.assertEquals(["https://www.upcast-project.eu/upcast-vocab/1.0/Integrate"],action_dependencies)
        action_dependencies = self.parser.get_action_dependencies(actionValue="http://www.w3.org/ns/odrl/aggregate")
        self.assertEquals(["http://www.w3.org/ns/odrl/anonymize"],action_dependencies)

    def test_get_action_no_dependencies(self):
        action_dependencies = self.parser.get_action_dependencies(actionValue="https://www.upcast-project.eu/upcast-vocab/1.0/Integrate")
        self.assertEquals([],action_dependencies)

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