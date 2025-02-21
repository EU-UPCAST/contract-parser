from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
import datetime
import logging
import sys

if sys.version_info[0] < 3:
    raise Exception("Python 3.11 or higher is required.")
if sys.version_info[1] < 11:
    raise Exception("Python 3.11 or higher is required.")


class ContractParser:
    IDSA = Namespace("https://w3id.org/idsa/core/")
    UPCAST = Namespace("https://www.upcast-project.eu/upcast-vocab/1.0/")

    def __init__(self):
        self.contract_graph = None

    def load(self, file_path):
        """
        Load the contract data from the specified file path.
        Returns an RDF graph object.
        """
        self.contract_graph = Graph().parse(file_path)
        self.contract_graph.bind("idsa-core", ContractParser.IDSA)
        self.contract_graph.bind("upcast", ContractParser.UPCAST)

    def query(self, query_string):
        """
        Query the loaded contract data with the specified SPARQL query string.
        """
        pass

    def get_contract_uri(self):
        """
        Convenience method to get the URI of the contract to use in other methods
        Assumption: A loaded document contains a single contract, hence a single contract URI
        Returns a rdflib Graph node
        """
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser") 
        contract_id = self.contract_graph.value(predicate=RDF.type, object=ContractParser.IDSA.Contract)
        return contract_id

    def get_provider(self):
        """
        Convenience method to get the provider of the contract
        """
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser") 
        provider = self.contract_graph.value(predicate=ContractParser.IDSA.Provider, subject=self.get_contract_uri())
        return provider
    
    def get_consumer(self):
        """
        Convenience method to get the provider of the contract
        """
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser") 
        consumer = self.contract_graph.value(predicate=ContractParser.IDSA.Consumer, subject=self.get_contract_uri())
        return consumer
    
    def get_permitted_actions(self):
        """
        Convenience method to get the permitted actions of the contract
        """
        
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser")
        
        # Permitted actions and their IRIs
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?actionIRI ?actionValue
        WHERE {
        ?agreement a odrl:Agreement ;
             odrl:permission ?permission .
        ?permission odrl:action ?actionIRI .
        ?actionIRI rdf:value ?actionValue .
        }
        """
        query_results = self.contract_graph.query(query)
        permitted_actions = {(row.actionIRI,str(row.actionValue)) for row in query_results}


        return permitted_actions
    
    def get_action_container(self,actionValue):
        """
        Input: action Value, i.e. , its name in String format
        Output: URL of the container that implements the input action IRI, None if not specified in the contract  
        """
        
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser")
        
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX upcast: <https://www.upcast-project.eu/upcast-vocab/1.0/> 

        SELECT ?rightOperand
        WHERE {
        ?actionIRI rdf:value ?actionValue .
        ?actionIRI odrl:refinement ?refinement .
        ?refinement odrl:leftOperand upcast:implementedBy ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand ?rightOperand .
        }
        """
        qres = self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)})
        qres_list = list(qres)

        return str(qres_list[0]["rightOperand"]) if len(qres) > 0 else None

    def get_action_execution_command(self,actionValue):
        """
        Input: action Value, i.e. , its name in String format
        Output: URL of the container that implements the input action IRI, None if not specified in the contract  
        """
        
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser")
        
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX upcast: <https://www.upcast-project.eu/upcast-vocab/1.0/> 

        SELECT ?rightOperand
        WHERE {
        ?actionIRI rdf:value ?actionValue .
        ?actionIRI odrl:refinement ?refinement .
        ?refinement odrl:leftOperand upcast:executionCommand ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand ?rightOperand .
        }
        """
        qres = self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)})
        qres_list = list(qres)

        return str(qres_list[0]["rightOperand"]) if len(qres) > 0 else None
    
    def get_action_execution_limits(self,actionValue):
        """
        input: actionValue, that is the name of the action in string format
        output: list of tuple of the form (operator, rightOperand) where operator is the comparison odrl operator (eq,lteq,gteq,gt) and rightOperand the integer value.
                An empty list is returned if the action does not have any execution limit
        """
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser")
        
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX upcast: <https://www.upcast-project.eu/upcast-vocab/1.0/> 

        SELECT ?operator ?rightOperand
        WHERE {
        ?actionIRI rdf:value ?actionValue .
        ?actionIRI odrl:refinement ?refinement .
        ?refinement odrl:leftOperand odrl:count ;
                    odrl:operator ?operator;
                    odrl:rightOperand ?rightOperand .
        }
        """
        qres = self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)})
        limits = []
        for row in qres:
            operator = str(row["operator"]).split("/")[-1]
            value = int(row["rightOperand"])
            limits.append((operator,value)) 

        return limits 
    
    def get_action_carbon_emission_limit(self,actionValue):
        """
        input: actionValue, that is the name of the action in string format
        output: Float value of maximum carbon emission agreed for this operation (that is, operator less ro equal than is assumed)
          returns None if there is no carbon emission limit defined in the contract
        """
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX upcast: <https://www.upcast-project.eu/upcast-vocab/1.0/> 

        SELECT ?rightOperand ?unit
        WHERE {
        ?actionIRI rdf:value ?actionValue .
        ?actionIRI odrl:constraint ?constraint .
        ?constraint odrl:leftOperand upcast:operationCarbonEmission ;
                    odrl:operator odrl:lteq;
                    odrl:rightOperand ?rightOperand;
                    odrl:unit ?unit  .
        }
        """
        qres = list(self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)}))
        if len(qres) == 0:
            return None
        result = qres[0]
        return (result["rightOperand"].toPython(),result["unit"].toPython())
    
    def get_action_energy_consumption_limit(self,actionValue):
        """
        input: actionValue, that is the name of the action in string format
        output: tuple (value,unit), with value a float of maximum energy consumption agreed for this operation (that is, operator less ro equal than is assumed)
             unit a string with the unit of the value
        """
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX upcast: <https://www.upcast-project.eu/upcast-vocab/1.0/> 

        SELECT ?rightOperand ?unit
        WHERE {
        ?actionIRI rdf:value ?actionValue .
        ?actionIRI odrl:constraint ?constraint .
        ?constraint odrl:leftOperand upcast:operationEnergyConsumption ;
                    odrl:operator odrl:lteq;
                    odrl:rightOperand ?rightOperand ;
                    odrl:unit ?unit  .
        }
        """
        qres = self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)})
        qres = list(self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)}))
        if len(qres) == 0:
            return None
        result = qres[0]
        return (result["rightOperand"].toPython(),result["unit"].toPython())
    
    def get_action_datetime_constraints(self,actionValue):
        """
        input: actionValue, that is the name of the action in string format
        output: list of tuple of the form (operator, datetime) where operator is the comparison odrl operator (eq,lt,lteq,gteq,gt) and datetime is the constrained datetime.
                An empty list is returned if the action does not have any datetime constraint.
        """
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX upcast: <https://www.upcast-project.eu/upcast-vocab/1.0/> 

        SELECT ?operator ?rightOperand
        WHERE {
        ?actionIRI rdf:value ?actionValue .
        ?actionIRI odrl:constraint ?constraint .
        ?constraint odrl:leftOperand odrl:dateTime ;
                    odrl:operator ?operator;
                    odrl:rightOperand ?rightOperand .
        }
        """
        qres = self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)})
        limits = []
        for row in qres:
            operator = str(row["operator"]).split("/")[-1]
            value = row["rightOperand"].toPython()
            limits.append((operator,value)) 
        return limits

    def get_action_dependencies(self,actionValue):
        """
        input: actionValue, that is the name of the action in string format
        output: list of actions that must be executed before the input action according to the loaded contract
        """
        if self.contract_graph is None:
            raise Exception("No contract loaded into this parser")
       
        # Note the permission and not the action is the one that has a duty
        query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX upcast: <https://www.upcast-project.eu/upcast-vocab/1.0/> 

        SELECT ?dependencyValue
        WHERE {
        ?agreement a odrl:Agreement ;
             odrl:permission ?permission .
        ?permission odrl:action ?actionIRI .
        ?actionIRI rdf:value ?actionValue .
        ?permission odrl:duty ?dutyIRI .
        ?dutyIRI odrl:action ?dependencyIRI .
        ?dependencyIRI rdf:value ?dependencyValue .
        }
        """

        qres = self.contract_graph.query(query,initBindings={'actionValue': URIRef(actionValue)})
        dependencies = [str(row["dependencyValue"]) for row in qres]
        return dependencies  

        


