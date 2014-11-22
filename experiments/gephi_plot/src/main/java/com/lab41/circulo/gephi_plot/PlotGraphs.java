package com.lab41.circulo.gephi_plot;
/*
 * Based on Gephi Headless Example by Mathieu Bastian (GPL v3)
*/

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;

import org.gephi.data.attributes.api.AttributeColumn;
import org.gephi.data.attributes.api.AttributeController;
import org.gephi.data.attributes.api.AttributeModel;
import org.gephi.graph.api.DirectedGraph;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2Builder;
import org.gephi.partition.api.NodePartition;
import org.gephi.partition.api.PartitionController;
import org.gephi.partition.plugin.NodeColorTransformer;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;

public class PlotGraphs {
	public static void main(String[] args){
		if(args.length != 2){
			System.err.println("Usage java -jar gephi_plot.jar <Directory with graphml files or graphml file> <output dir>");
			System.exit(65);
		}
		
		ArrayList<String> filesToProcess = new ArrayList<String>();
		File inputPath = new File(args[0]);
		if (inputPath.exists()){
			// If input is a single file add that and continue
			if (inputPath.isFile()){
				filesToProcess.add(inputPath.getPath());
			// For each input file process output
			}else{
				for (String filePath: inputPath.list()){
					if (filePath.endsWith(".graphml") == true){
						String fullFilePath = Paths.get(inputPath.getPath(), filePath).toString();
						filesToProcess.add(fullFilePath);
					}
				}
			}		
		}else{
			System.err.println("Input path does not exist: " + args[0]);
			System.exit(65);
		}
		
		for (String fileToProcess: filesToProcess){
			PlotGraphs hs = new PlotGraphs();
			hs.script(fileToProcess, args[1]);
		}
	}
	

	public void script(String graphPath, String outputPath) {
		// Extract dataset name
		String graphFileName = new File(graphPath).getName();
		String datasetName = graphFileName.substring(0, graphFileName.indexOf(".graphml"));
		
		// Initialize a Gephi project and workspace
		ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
		pc.newProject();
		Workspace workspace = pc.getCurrentWorkspace();

		// Get models and controllers for this new workspace - will be useful later
		AttributeModel attributeModel = Lookup.getDefault().lookup(AttributeController.class).getModel();
		GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getModel();
		PreviewModel model = Lookup.getDefault().lookup(PreviewController.class).getModel();
		ImportController importController = Lookup.getDefault().lookup(ImportController.class);
		PartitionController partitionController = Lookup.getDefault().lookup(PartitionController.class); 

		// Import file       
		Container container;
		try {
			File file = new File(graphPath);
			container = importController.importFile(file);
		} catch (Exception ex) {
			ex.printStackTrace();
			return;
		}

		// Append imported data to GraphAPI
		importController.process(container, new DefaultProcessor(), workspace);

		// See if graph is well imported
		DirectedGraph graph = graphModel.getDirectedGraph();

		// Do ForceAtlas2 based layout
		ForceAtlas2Builder fa2b = new ForceAtlas2Builder();
		ForceAtlas2 fa2Layout = fa2b.buildLayout();
		fa2Layout.setGraphModel(graphModel);
		fa2Layout.setThreadsCount(Runtime.getRuntime().availableProcessors()); 
		fa2Layout.initAlgo();
		int i_max = 1000; // TODO: Look into setting this more intelligently (some sort of convergence metric)
		long startTime = System.currentTimeMillis();
		long currentTime = System.currentTimeMillis();
		for (int i = 0; i < i_max && fa2Layout.canAlgo() && currentTime - startTime < 1000*60*10 ; i++) {
			// Want to take faster steps at first but then be more careful
			if (i < i_max/4.0){
				fa2Layout.setJitterTolerance(1.0);
			}else{
				fa2Layout.setJitterTolerance(0.1);
			}
			fa2Layout.goAlgo();
			currentTime = System.currentTimeMillis();
		}
		fa2Layout.endAlgo();

		// Figure out which algorithms are in the results set
		ArrayList<String> algoResultsPresent = new ArrayList<String>();
		for(AttributeColumn ac: attributeModel.getNodeTable().getColumns()){
			String title = ac.getTitle();
			if (title.startsWith("algo")){
				algoResultsPresent.add(ac.getTitle());
			}
		}
		
		// For each algorithm, create an output of the results
		for (String algoResult: algoResultsPresent){
			System.out.println("Printing: " + algoResult);
			NodePartition p = (NodePartition) partitionController.buildPartition(attributeModel.getNodeTable().getColumn(algoResult), graph);
			NodeColorTransformer nodeColorTransformer = new NodeColorTransformer();
			nodeColorTransformer.randomizeColors(p);
			partitionController.transform(p, nodeColorTransformer);

			// Don't show node labels, make edges straight lines
			model.getProperties().putValue(PreviewProperty.SHOW_NODE_LABELS, Boolean.FALSE);
			model.getProperties().putValue(PreviewProperty.EDGE_CURVED, Boolean.FALSE);

			// Export to PDF file
			ExportController ec = Lookup.getDefault().lookup(ExportController.class);
			try {
				String outputFileName = datasetName + "_"+algoResult+".pdf";
				ec.exportFile(Paths.get(outputPath, outputFileName).toFile());
			} catch (IOException ex) {
				ex.printStackTrace();
				return;
			}
		}

	}
}