<?php
include("../../../config/settings.inc.php");
include("../../../include/database.inc.php");
$connection = iemdb("isuag");
include("../../../include/network.php");
$nt = new NetworkTable("ISUAG");
$ISUAGcities = $nt->table;

$station = $_GET['station'];
$ts = time() - 86400 - 7*3600;
$table = "hourly";
$date = date("Y-m-d", $ts);


$rs = pg_prepare($connection, "SELECT", " SELECT c100 as dater, c300 as dater2, " .
		"c800, to_char(valid, 'mmdd/HH24') as valid from hourly WHERE " .
		"station = $1 and date(valid) = $2 ORDER by valid ASC");

$result = pg_execute($connection, "SELECT", Array($station, $date));

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["c800"];
  $ydata2[$i]  = $row["dater"];
  $ydata3[$i] = $row["dater2"];
  $xlabel[$i] = $row["valid"];
}


pg_close($connection);

include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("textlin");
$graph->SetY2Scale("lin",0,1000);
$graph->img->SetMargin(50,40,45,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set($date ." Solar Rad & Temps for  ". $ISUAGcities[$station]["name"] );

$graph->y2axis->scale->ticks->Set(100,50);


$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->SetTitle("Solar Radiation [kilo-calorie m**-2]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->yaxis->SetTitle("Temperature [F]");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(55);
$graph->yaxis->SetTitleMargin(37);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

//$graph->y2axis->SetColor("blue");
$graph->y2axis->SetColor("red");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$graph->AddY2($lineplot);
$lineplot->SetColor("red");
$lineplot->SetLegend("Solar Rad");
$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$graph->Add($lineplot2);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("Air Temp");
$lineplot2->SetWeight(2);

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$graph->Add($lineplot3);
$lineplot3->SetColor("green");
$lineplot3->SetLegend("4in Soil Temp");
$lineplot3->SetWeight(2);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


$graph->Stroke();
?>

