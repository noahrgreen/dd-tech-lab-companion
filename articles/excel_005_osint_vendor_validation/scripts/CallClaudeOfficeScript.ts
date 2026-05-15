
function main(workbook: ExcelScript.Workbook) {
  const sheet = workbook.getWorksheet('Parameters');
  const apiKey = sheet.getRange('B2').getValue();
  console.log(`Placeholder Office Script invoked. API key configured: ${apiKey !== 'ENTER_API_KEY_HERE'}`);
}
