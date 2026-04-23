<?php
// api.php — returns latest seismic data as JSON

header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");

$host   = "localhost";
$user   = "root";
$pass   = "";
$dbname = "quakesense";

$conn = new mysqli($host, $user, $pass, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "DB connection failed: " . $conn->connect_error]);
    exit;
}

// Latest 50 records (newest first)
$sql    = "SELECT id, status, diff_value, recorded_at FROM seismic_data ORDER BY recorded_at DESC LIMIT 50";
$result = $conn->query($sql);

$rows = [];
while ($row = $result->fetch_assoc()) {
    $rows[] = $row;
}

// Stats
$statsSql  = "SELECT 
    COUNT(*) as total,
    SUM(status = 'WARNING') as warnings,
    SUM(status = 'EARTHQUAKE!') as earthquakes,
    MAX(diff_value) as max_diff
FROM seismic_data";

$statsResult = $conn->query($statsSql);
$stats       = $statsResult->fetch_assoc();

echo json_encode([
    "records" => $rows,
    "stats"   => $stats
]);

$conn->close();
?>