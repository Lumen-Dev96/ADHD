import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONException;
import com.alibaba.fastjson.JSONObject;

import java.io.*;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.*;

public class MyTcp {
    //        private static String remoteTcpAddress = "192.168.0.6";
    private static String remoteTcpAddress = "192.168.4.1"; // given that the remote address is 192.168.4.1
    private static int remoteTcpPort = 31415; //  given that the remote port  is 192.168.4.1

    private static Map<String, String> coordinateMap = new HashMap<>();
    private static boolean isNeedFilter = true; // 是否导出滤波数据到csv
    private static boolean isNeedRemoveBaseline = true; // 是否导出滤波数据到csv

    private static Socket socket; //
    private static OutputStream TCP_outputStream;
    private static InputStream TCP_inputStream;
    private static int errorCnt = 0; //
    private static double MPU_AccelResolution = 16 * 9.8 / 32768.0; //
    private static double MPU_GyroResolution = 2000 / 32768.0; //
    public static ArrayList ACCEL1Total = new ArrayList();
    public static ArrayList GYRO1Total = new ArrayList();
    public static ArrayList ACCEL2Total = new ArrayList();
    public static ArrayList GYRO2Total = new ArrayList();
    public static List<Long> timeTotal = new LinkedList<>();
    private static boolean isTiming = false;
    private static int x1Index = 0;
    private static int y1Index = 1;
    private static int z1Index = 2;
    private static int x1Multiplier = 1;
    private static int y1Multiplier = 1;
    private static int z1Multiplier = 1;
    private static int x2Index = 0;
    private static int y2Index = 1;
    private static int z2Index = 2;
    private static int x2Multiplier = 1;
    private static int y2Multiplier = 1;
    private static int z2Multiplier = 1;


    public static void main(String[] args) { // main function
        JSONObject config = readConfig();
        coordinateMap.put("targetX1", config.getString("targetX1")); // pair up the label and the data value
        coordinateMap.put("targetY1", config.getString("targetY1"));
        coordinateMap.put("targetZ1", config.getString("targetZ1"));
        coordinateMap.put("targetX2", config.getString("targetX2"));
        coordinateMap.put("targetY2", config.getString("targetY2"));
        coordinateMap.put("targetZ2", config.getString("targetZ2"));
        isNeedFilter = config.getBooleanValue("isNeedFilter");
        isNeedRemoveBaseline = config.getBooleanValue("isNeedRemoveBaseline");
        setCoordinateMap();//
        connectTCP();//  handle the input and output issue between server and imu
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {

        }
        String sendBuffer = "";
        Scanner s = new Scanner(System.in);// get the jason file as command
        SimpleDateFormat sf = new SimpleDateFormat("HH:mm:ss.SSS\t");

        Timer timer = new Timer();
        TimerTask task = null;
        System.out.println("Inint successfully"); // ensure the init state successful
        while (true) {
            sendBuffer = s.nextLine();
            JSONObject command = JSON.parseObject(sendBuffer);
            String function = command.getString("func");

            try {
                if (function.equals("StartCollect")) {
                    if (isTiming) {
                        task.cancel();
                        isTiming = false;
                    }
                    ACCEL1Total.clear();
                    GYRO1Total.clear();
                    ACCEL2Total.clear();
                    GYRO2Total.clear();
                    timeTotal.clear();
                    sendTcpMessage(sendBuffer);
                    if (command.containsKey("autoStopTime")) {
                        int autoStopTime = command.getIntValue("autoStopTime");
                        System.out.println("将在" + autoStopTime + "秒后自动停止采集！");
                        System.out.println(sf.format(new Date()));
                        task = new TimerTask() {
                            @Override
                            public void run() {
                                this.cancel();
                                sendTcpMessage("{\"func\":\"StopCollect\"}");
                                System.out.println(sf.format(new Date()));
                                System.out.println("Saving the data...");
                                try {
                                    Thread.sleep(2000);
                                } catch (InterruptedException e) {
                                }
                                saveDataToTxt(); // save all the data to txt file
                                exportCSV();// save all the data to csv file
                                if (isNeedFilter)
                                    exportFilterCSV();
                                if (isNeedRemoveBaseline)
                                    exportRemoveBaselineCSV();
                                if (isNeedFilter && isNeedRemoveBaseline)
                                    exportFilterRemoveBaselineCSV();
                                System.out.println("--------All data is exported--------");
                                isTiming = false;
                            }
                        };
                        timer.schedule(task, autoStopTime * 1000);
                        isTiming = true;
                    }

                } else if (function.equals("StopCollect")) {
                    // final command to stop collect
                    if (isTiming) {
                        task.cancel();
                        isTiming = false;
                    }
                    sendTcpMessage(sendBuffer);
                    System.out.println("Saving the data...");
                    try {
                        Thread.sleep(1000);
                    } catch (InterruptedException e) {
                    }
                    saveDataToTxt();
                    exportCSV();
                    if (isNeedFilter)
                        exportFilterCSV();
                    if (isNeedRemoveBaseline)
                        exportRemoveBaselineCSV();
                    if (isNeedFilter && isNeedRemoveBaseline)
                        exportFilterRemoveBaselineCSV();
                    System.out.println("--------All data is exported--------");
                } else {
                    sendTcpMessage(sendBuffer);
                }

            }catch(Exception E){
                System.out.println(E);
                System.out.println("PLEASE CHECK THE SET UP OF THE HARDWARE.... ");
                break; // End the while loop
            }finally {
                // call back up function
                //saveDataToTxt();
                //exportCSV();
            }

        }
    }

    public static JSONObject readConfig() {
        try {
            File file = new File("./src/config.json");
            FileReader fileReader = new FileReader(file);
            BufferedReader buffReader = new BufferedReader(fileReader);
            StringBuffer sb = new StringBuffer();
            String line = "";
            while ((line = buffReader.readLine()) != null) {
                sb.append(line);
            }
            buffReader.close();
            fileReader.close();
            JSONObject config = JSON.parseObject(sb.toString());
            return config;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    //private static void saveDataToTxt() {
    //   StringBuffer MPUData = new StringBuffer();
    //   SimpleDateFormat sf = new SimpleDateFormat("[yyyyMMdd HH:mm:ss:SSS] | ");
    //   MPUData.append(" 时间  |  传感器1加速度（m/s^2）  |  传感器2加速度（m/s^2）  |  传感器1角速度（°/s）  |  传感器2角速度（°/s）\r\n");
    //   MPUData.append("[采样时间] | [ Ax1 , Ay1 , Az1 ] | [ Ax2 , Ay2 , Az2 ] | [ Gx1 , Gy1 , Gz1 ] | [ Gx2 , Gy2 , Gz2 ]\r\n");
    //    List<Integer> lenList = new LinkedList<>();
    //  lenList.add(ACCEL1Total.size());
    //  lenList.add(ACCEL2Total.size());
    //  lenList.add(GYRO1Total.size());
    //  lenList.add(GYRO2Total.size());
    //   int len = Collections.min(lenList);
    //  long time = startDate.getTime();
    //   for (int i = 0; i < len; i++) {
    //      MPUData.append(sf.format(time));
    //    time += 10;
    //       List<Float> accel1 = (List<Float>) ACCEL1Total.get(i);
    //      List<Float> accel2 = (List<Float>) ACCEL2Total.get(i);
    //       List<Float> gyro1 = (List<Float>) GYRO1Total.get(i);
    //      List<Float> gyro2 = (List<Float>) GYRO2Total.get(i);
    //         String accel1Str = String.format("[%.2f, %.2f, %.2f] | ", accel1.get(0), accel1.get(1), accel1.get(2));
    //    String accel2Str = String.format("[%.2f, %.2f, %.2f] | ", accel2.get(0), accel2.get(1), accel2.get(2));
    //    String gyro1Str = String.format("[%.2f, %.2f, %.2f] | ", gyro1.get(0), gyro1.get(1), gyro1.get(2));
    //      String gyro2Str = String.format("[%.2f, %.2f, %.2f]\r\n", gyro2.get(0), gyro2.get(1), gyro2.get(2));
    //      MPUData.append(accel1Str + accel2Str + gyro1Str + gyro2Str);
    //   }
    //   SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_hhmmss");
    //    saveTxt("./data/MPUData_" + sdf.format(new Date()) + ".txt", MPUData.toString());
    //}

    private static void saveDataToTxt() {
        StringBuffer MPUData = new StringBuffer();
        SimpleDateFormat sf = new SimpleDateFormat("yyyyMMdd HH:mm:ss.SSS\t");
        MPUData.append(" 时间  |  传感器1加速度（m/s^2）  |  传感器2加速度（m/s^2）  |  传感器1角速度（°/s）  |  传感器2角速度（°/s）\r\n");
        MPUData.append("采样时间\tAx1\tAy1\tAz1\tAx2\tAy2\tAz2\tGx1\tGy1\tGz1\tGx2\tGy2\tGz2\r\n");
        List<Integer> lenList = new LinkedList<>();
        lenList.add(ACCEL1Total.size());
        lenList.add(ACCEL2Total.size());
        lenList.add(GYRO1Total.size());
        lenList.add(GYRO2Total.size());
        int len = Collections.min(lenList); // ensure all data can pair up together

        for (int i = 0; i < len; i++) {
            MPUData.append(sf.format(timeTotal.get(i))); // get the related time stamp of i
            List<Float> accel1 = (List<Float>) ACCEL1Total.get(i);
            List<Float> accel2 = (List<Float>) ACCEL2Total.get(i);
            List<Float> gyro1 = (List<Float>) GYRO1Total.get(i);
            List<Float> gyro2 = (List<Float>) GYRO2Total.get(i);
            // get all the data at time i
            String accel1Str = String.format("%.2f\t%.2f\t%.2f\t", accel1.get(x1Index) * x1Multiplier, accel1.get(y1Index) * y1Multiplier, accel1.get(z1Index) * z1Multiplier);
            String accel2Str = String.format("%.2f\t%.2f\t%.2f\t", accel2.get(x2Index) * x2Multiplier, accel2.get(y2Index) * y2Multiplier, accel2.get(z2Index) * z2Multiplier);
            String gyro1Str = String.format("%.2f\t%.2f\t%.2f\t", gyro1.get(x1Index) * x1Multiplier, gyro1.get(y1Index) * y1Multiplier, gyro1.get(z1Index) * z1Multiplier);
            String gyro2Str = String.format("%.2f\t%.2f\t%.2f\r\n", gyro2.get(x2Index) * x2Multiplier, gyro2.get(y2Index) * y2Multiplier, gyro2.get(z2Index) * z2Multiplier);
            MPUData.append(accel1Str + accel2Str + gyro1Str + gyro2Str); // group the data together
        }
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss");
        saveTxt("./data/MPUData_" + sdf.format(timeTotal.get(0)) + ".txt", MPUData.toString());// wrong may happen

    }

    public static void saveTxt(String outputPathName, String data) {
        File file = new File(outputPathName);// create file object with a given path
        try {
            file.createNewFile();// create file
            FileWriter fileWriter = new FileWriter(file); // create file writer
            fileWriter.write(data); // write the data to the file
            fileWriter.close(); // close the file
            System.out.println("The txt export success\nThe save path is:" + outputPathName);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


    public static void exportCSV() {
        String filePath = "./CSV/";
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss");
        String fileName = "MPUData_" + sdf.format(timeTotal.get(0));
        List<Object> titleList = new LinkedList<>();
        titleList.add("time");
        titleList.add("Ax1");
        titleList.add("Ay1");
        titleList.add("Az1");
        titleList.add("Ax2");
        titleList.add("Ay2");
        titleList.add("Az2");
        titleList.add("Gx1");
        titleList.add("Gy1");
        titleList.add("Gz1");
        titleList.add("Gx2");
        titleList.add("Gy2");
        titleList.add("Gz2");

        List<List<Object>> colList = new LinkedList<>();

        SimpleDateFormat sf = new SimpleDateFormat("yyyyMMdd HH:mm:ss.SSS\t");

        List<Integer> lenList = new LinkedList<>();
        lenList.add(ACCEL1Total.size());
        lenList.add(ACCEL2Total.size());
        lenList.add(GYRO1Total.size());
        lenList.add(GYRO2Total.size());
        int len = Collections.min(lenList);
        for (int i = 0; i < len; i++) {

            List<Object> rowList = new LinkedList<>();
            rowList.add(sf.format(timeTotal.get(i)));

            List<Float> accel1 = (List<Float>) ACCEL1Total.get(i);
            List<Float> accel2 = (List<Float>) ACCEL2Total.get(i);
            List<Float> gyro1 = (List<Float>) GYRO1Total.get(i);
            List<Float> gyro2 = (List<Float>) GYRO2Total.get(i);
            List<Float> lineData = new LinkedList<>();
            lineData.add(accel1.get(x1Index) * x1Multiplier);
            lineData.add(accel1.get(y1Index) * y1Multiplier);
            lineData.add(accel1.get(z1Index) * z1Multiplier);
            lineData.add(accel2.get(x2Index) * x2Multiplier);
            lineData.add(accel2.get(y2Index) * y2Multiplier);
            lineData.add(accel2.get(z2Index) * z2Multiplier);
            lineData.add(gyro1.get(x1Index) * x1Multiplier);
            lineData.add(gyro1.get(y1Index) * y1Multiplier);
            lineData.add(gyro1.get(z1Index) * z1Multiplier);
            lineData.add(gyro2.get(x2Index) * x2Multiplier);
            lineData.add(gyro2.get(y2Index) * y2Multiplier);
            lineData.add(gyro2.get(z2Index) * z2Multiplier);
            for (int j = 0; j < 12; j++) {
                rowList.add(String.format("%.2f", lineData.get(j)));
            }
            colList.add(rowList);
        }
        CsvFile.export(filePath, fileName, titleList, colList); // use Csv class static to method handle the bunch of data
        System.out.println("Export:" + filePath + fileName + ".csv");
    }

    public static void exportFilterCSV() {
        String filePath = "./CSV/";
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss");
        String fileName = "MPUData_" + sdf.format(timeTotal.get(0)) + "_Filter";
        List<Object> titleList = new LinkedList<>();
        titleList.add("采样时间");
        titleList.add("Ax1_F");
        titleList.add("Ay1_F");
        titleList.add("Az1_F");
        titleList.add("Ax2_F");
        titleList.add("Ay2_F");
        titleList.add("Az2_F");
        titleList.add("Gx1_F");
        titleList.add("Gy1_F");
        titleList.add("Gz1_F");
        titleList.add("Gx2_F");
        titleList.add("Gy2_F");
        titleList.add("Gz2_F");
        KalmanFilter[] filters = new KalmanFilter[12];

        for (int i = 0; i < 12; i++) {
            filters[i] = new KalmanFilter();
        }

        List<List<Object>> colList = new LinkedList<>();

        SimpleDateFormat sf = new SimpleDateFormat("yyyyMMdd HH:mm:ss.SSS\t");

        List<Integer> lenList = new LinkedList<>();
        lenList.add(ACCEL1Total.size());
        lenList.add(ACCEL2Total.size());
        lenList.add(GYRO1Total.size());
        lenList.add(GYRO2Total.size());
        int len = Collections.min(lenList);
        for (int i = 0; i < len; i++) {

            List<Object> rowList = new LinkedList<>();
            rowList.add(sf.format(timeTotal.get(i)));
            //  读取一次采集的数据
            List<Float> accel1 = (List<Float>) ACCEL1Total.get(i);
            List<Float> accel2 = (List<Float>) ACCEL2Total.get(i);
            List<Float> gyro1 = (List<Float>) GYRO1Total.get(i);
            List<Float> gyro2 = (List<Float>) GYRO2Total.get(i);

            //把每一个数据加入到List中
            List<Float> lineData = new LinkedList<>();
            lineData.add(accel1.get(x1Index) * x1Multiplier);
            lineData.add(accel1.get(y1Index) * y1Multiplier);
            lineData.add(accel1.get(z1Index) * z1Multiplier);
            lineData.add(accel2.get(x2Index) * x2Multiplier);
            lineData.add(accel2.get(y2Index) * y2Multiplier);
            lineData.add(accel2.get(z2Index) * z2Multiplier);
            lineData.add(gyro1.get(x1Index) * x1Multiplier);
            lineData.add(gyro1.get(y1Index) * y1Multiplier);
            lineData.add(gyro1.get(z1Index) * z1Multiplier);
            lineData.add(gyro2.get(x1Index) * x2Multiplier);
            lineData.add(gyro2.get(y1Index) * y2Multiplier);
            lineData.add(gyro2.get(z1Index) * z2Multiplier);

            List<Float> lineFilterData = new LinkedList<>();

            // 对每一个数据进行滤波
            for (int j = 0; j < 6; j++) {
                lineFilterData.add(filters[j].getAccel(lineData.get(j)));
            }
            for (int j = 6; j < 12; j++) {
                lineFilterData.add(filters[j].getGyro(lineData.get(j)));
            }

            // 格式化每个数据，为填入每单元格做准备
            for (int j = 0; j < 12; j++) {
                rowList.add(String.format("%.2f", lineFilterData.get(j)));
            }
            colList.add(rowList);
        }
        CsvFile.export(filePath, fileName, titleList, colList);
        System.out.println("Export:" + filePath + fileName + ".csv");
    }

    public static void exportRemoveBaselineCSV() {
        String filePath = "./CSV/";
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss");
        String fileName = "MPUData_" + sdf.format(timeTotal.get(0)) + "_RemoveBaseline";
        List<Object> titleList = new LinkedList<>();
        titleList.add("采样时间");
        titleList.add("Ax1_R");
        titleList.add("Ay1_R");
        titleList.add("Az1_R");
        titleList.add("Ax2_R");
        titleList.add("Ay2_R");
        titleList.add("Az2_R");
        titleList.add("Gx1_R");
        titleList.add("Gy1_R");
        titleList.add("Gz1_R");
        titleList.add("Gx2_R");
        titleList.add("Gy2_R");
        titleList.add("Gz2_R");

        List<List<Object>> colList = new LinkedList<>();

        SimpleDateFormat sf = new SimpleDateFormat("yyyyMMdd HH:mm:ss.SSS\t");

        float accel1x = ((List<Float>) ACCEL1Total.get(0)).get(x1Index) * x1Multiplier;
        float accel1y = ((List<Float>) ACCEL1Total.get(0)).get(y1Index) * y1Multiplier;
        float accel1z = ((List<Float>) ACCEL1Total.get(0)).get(z1Index) * z1Multiplier;
        float accel2x = ((List<Float>) ACCEL2Total.get(0)).get(x2Index) * x2Multiplier;
        float accel2y = ((List<Float>) ACCEL2Total.get(0)).get(y2Index) * y2Multiplier;
        float accel2z = ((List<Float>) ACCEL2Total.get(0)).get(z2Index) * z2Multiplier;
        float gyro1x = ((List<Float>) GYRO1Total.get(0)).get(x1Index) * x1Multiplier;
        float gyro1y = ((List<Float>) GYRO1Total.get(0)).get(y1Index) * y1Multiplier;
        float gyro1z = ((List<Float>) GYRO1Total.get(0)).get(z1Index) * z1Multiplier;
        float gyro2x = ((List<Float>) GYRO2Total.get(0)).get(x2Index) * x2Multiplier;
        float gyro2y = ((List<Float>) GYRO2Total.get(0)).get(y2Index) * y2Multiplier;
        float gyro2z = ((List<Float>) GYRO2Total.get(0)).get(z2Index) * z2Multiplier;
        List<Integer> lenList = new LinkedList<>();
        lenList.add(ACCEL1Total.size());
        lenList.add(ACCEL2Total.size());
        lenList.add(GYRO1Total.size());
        lenList.add(GYRO2Total.size());
        int len = Collections.min(lenList);
        for (int i = 0; i < len; i++) {

            List<Object> rowList = new LinkedList<>();
            rowList.add(sf.format(timeTotal.get(i)));

            List<Float> accel1 = (List<Float>) ACCEL1Total.get(i);
            List<Float> accel2 = (List<Float>) ACCEL2Total.get(i);
            List<Float> gyro1 = (List<Float>) GYRO1Total.get(i);
            List<Float> gyro2 = (List<Float>) GYRO2Total.get(i);

            List<Float> lineData = new LinkedList<>();
            lineData.add(accel1.get(x1Index) * x1Multiplier - accel1x);
            lineData.add(accel1.get(y1Index) * y1Multiplier - accel1y);
            lineData.add(accel1.get(z1Index) * z1Multiplier - accel1z);
            lineData.add(accel2.get(x2Index) * x2Multiplier - accel2x);
            lineData.add(accel2.get(y2Index) * y2Multiplier - accel2y);
            lineData.add(accel2.get(z2Index) * z2Multiplier - accel2z);
            lineData.add(gyro1.get(x1Index) * x1Multiplier - gyro1x);
            lineData.add(gyro1.get(y1Index) * y1Multiplier - gyro1y);
            lineData.add(gyro1.get(z1Index) * z1Multiplier - gyro1z);
            lineData.add(gyro2.get(x2Index) * x2Multiplier - gyro2x);
            lineData.add(gyro2.get(y2Index) * y2Multiplier - gyro2y);
            lineData.add(gyro2.get(z2Index) * z2Multiplier - gyro2z);
            for (int j = 0; j < 12; j++) {
                rowList.add(String.format("%.2f", lineData.get(j)));
            }
            colList.add(rowList);
        }
        CsvFile.export(filePath, fileName, titleList, colList);// easy to have error
        System.out.println("Export:" + filePath + fileName + ".csv");
    }

    public static void exportFilterRemoveBaselineCSV() {
        String filePath = "./CSV/";
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd_HHmmss");
        String fileName = "MPUData_" + sdf.format(timeTotal.get(0)) + "_FilterRemoveBaseline";
        List<Object> titleList = new LinkedList<>();
        titleList.add("采样时间");
        titleList.add("Ax1_FR");
        titleList.add("Ay1_FR");
        titleList.add("Az1_FR");
        titleList.add("Ax2_FR");
        titleList.add("Ay2_FR");
        titleList.add("Az2_FR");
        titleList.add("Gx1_FR");
        titleList.add("Gy1_FR");
        titleList.add("Gz1_FR");
        titleList.add("Gx2_FR");
        titleList.add("Gy2_FR");
        titleList.add("Gz2_FR");
        KalmanFilter[] filters = new KalmanFilter[12];

        for (int i = 0; i < 12; i++) {
            filters[i] = new KalmanFilter();
        }

        List<List<Object>> colList = new LinkedList<>();

        SimpleDateFormat sf = new SimpleDateFormat("yyyyMMdd HH:mm:ss.SSS\t");

        List<Integer> lenList = new LinkedList<>();
        lenList.add(ACCEL1Total.size());
        lenList.add(ACCEL2Total.size());
        lenList.add(GYRO1Total.size());
        lenList.add(GYRO2Total.size());
        int len = Collections.min(lenList);
        float[] baselineData = new float[12];
        for (int i = 0; i < len; i++) {

            List<Object> rowList = new LinkedList<>();
            rowList.add(sf.format(timeTotal.get(i)));
            //  读取一次采集的数据
            List<Float> accel1 = (List<Float>) ACCEL1Total.get(i);
            List<Float> accel2 = (List<Float>) ACCEL2Total.get(i);
            List<Float> gyro1 = (List<Float>) GYRO1Total.get(i);
            List<Float> gyro2 = (List<Float>) GYRO2Total.get(i);

            //把每一个数据加入到List中
            List<Float> lineData = new LinkedList<>();
            lineData.add(accel1.get(x1Index) * x1Multiplier);
            lineData.add(accel1.get(y1Index) * y1Multiplier);
            lineData.add(accel1.get(z1Index) * z1Multiplier);
            lineData.add(accel2.get(x2Index) * x2Multiplier);
            lineData.add(accel2.get(y2Index) * y2Multiplier);
            lineData.add(accel2.get(z2Index) * z2Multiplier);
            lineData.add(gyro1.get(x1Index) * x1Multiplier);
            lineData.add(gyro1.get(y1Index) * y1Multiplier);
            lineData.add(gyro1.get(z1Index) * z1Multiplier);
            lineData.add(gyro2.get(x2Index) * x2Multiplier);
            lineData.add(gyro2.get(y2Index) * y2Multiplier);
            lineData.add(gyro2.get(z2Index) * z2Multiplier);

            List<Float> lineFilterData = new LinkedList<>();


            // 对每一个数据进行滤波
            for (int j = 0; j < 6; j++) {
                if (i == 0) {
                    baselineData[j] = filters[j].getAccel(lineData.get(j));
                    lineFilterData.add(0f);
                } else
                    lineFilterData.add(filters[j].getAccel(lineData.get(j)) - baselineData[j]);
            }
            for (int j = 6; j < 12; j++) {
                if (i == 0) {
                    baselineData[j] = filters[j].getAccel(lineData.get(j));
                    lineFilterData.add(0f);
                } else
                    lineFilterData.add(filters[j].getGyro(lineData.get(j)) - baselineData[j]);
            }

            // 格式化每个数据，为填入每单元格做准备
            for (int j = 0; j < 12; j++) {
                rowList.add(String.format("%.2f", lineFilterData.get(j)));
            }
            colList.add(rowList);
        }
        CsvFile.export(filePath, fileName, titleList, colList);
        System.out.println("Export:" + filePath + fileName + ".csv");
    }

    public static void setCoordinateMap() {
        //坐标轴映射
        String lastCh = coordinateMap.get("targetX1");
        lastCh = lastCh.substring(lastCh.length() - 1);
        x1Index = 0;
        if (lastCh.equals("Y"))
            x1Index = 1;
        else if (lastCh.equals("Z")) {
            x1Index = 2;
        }
        x1Multiplier = coordinateMap.get("targetX1").charAt(0) == '-' ? -1 : 1;

        lastCh = coordinateMap.get("targetY1");
        lastCh = lastCh.substring(lastCh.length() - 1);
        y1Index = 1;
        if (lastCh.equals("X"))
            y1Index = 0;
        else if (lastCh.equals("Z")) {
            y1Index = 2;
        }
        y1Multiplier = coordinateMap.get("targetY1").charAt(0) == '-' ? -1 : 1;

        lastCh = coordinateMap.get("targetZ1");
        lastCh = lastCh.substring(lastCh.length() - 1);
        z1Index = 2;
        if (lastCh.equals("X"))
            z1Index = 0;
        else if (lastCh.equals("Y")) {
            z1Index = 1;
        }
        z1Multiplier = coordinateMap.get("targetZ1").charAt(0) == '-' ? -1 : 1;


        lastCh = coordinateMap.get("targetX2");
        lastCh = lastCh.substring(lastCh.length() - 1);
        x2Index = 0;
        if (lastCh.equals("Y"))
            x2Index = 1;
        else if (lastCh.equals("Z")) {
            x2Index = 2;
        }
        x2Multiplier = coordinateMap.get("targetX2").charAt(0) == '-' ? -1 : 1;

        lastCh = coordinateMap.get("targetY2");
        lastCh = lastCh.substring(lastCh.length() - 1);
        y2Index = 1;
        if (lastCh.equals("X"))
            y2Index = 0;
        else if (lastCh.equals("Z")) {
            y2Index = 2;
        }
        y2Multiplier = coordinateMap.get("targetY2").charAt(0) == '-' ? -1 : 1;

        lastCh = coordinateMap.get("targetZ2");
        lastCh = lastCh.substring(lastCh.length() - 1);
        z2Index = 2;
        if (lastCh.equals("X"))
            z2Index = 0;
        else if (lastCh.equals("Y")) {
            z2Index = 1;
        }
        z2Multiplier = coordinateMap.get("targetZ2").charAt(0) == '-' ? -1 : 1;
    }

    private static void connectTCP() {
        new Thread() { //
            @Override
            public void run() {
                try {
                    socket = new Socket(remoteTcpAddress, remoteTcpPort); // use the given address and port to create socket for commucnication purpose
                    TCP_inputStream = socket.getInputStream();// for recieving input
                    TCP_outputStream = socket.getOutputStream();// for sending  output
                    readServerCallBack(); // refer to the bellow method
                    System.out.println("TCP connection success!");
                    sendTcpMessage("TCP Connection!");
                } catch (Exception e) {
                    System.out.println("Fail to connect TCP....");
                }
            }
        }.start(); // create a thread with defined method and start working
    }


    public static void readServerCallBack() {

        new Thread() {
            @Override
            public void run() {
                boolean isWhile = true;
                int Number_ofcollected_data=0;
                while (isWhile) {
                    try {
                        byte[] b = new byte[10000]; // declare a byte array to read message
                        TCP_inputStream.read(b);// get the message
                        String Msg = new String(b).trim(); // convert the byte array to string
                        //System.out.println("the data collection thread recieved "+Msg);
                        JSONObject jsonObject; // create a json object
                        try {
                            jsonObject = JSONObject.parseObject(Msg); // convert the message to json format
                        } catch (JSONException e) {
                            e.printStackTrace(); // if JSONException is caught print error message and keep going
                            System.out.println("Error message:" + Msg);
                            continue;
                        }
                        //System.out.println("The command of json "+jsonObject);
                        String func = jsonObject.getString("func");  //
                        String[] gyro1s=null;
                        String[] gyro2s=null;
                        float accel1_Data=0;
                        float accel2_Data=0;
                        String temp_Data=null;
                        if (func.equals("receiveData")) {
                            String accel1Str = jsonObject.getString("accel1Str");
                            String accel2Str = jsonObject.getString("accel2Str");
                            String gyro1Str = jsonObject.getString("gyro1Str");// easy to get error
                            String gyro2Str = jsonObject.getString("gyro2Str");// java.lang.NullPointerException: Cannot invoke "String.split(String)" because "gyro1Str" is null

                            String[] accel1s = accel1Str.split(",");
                            String[] accel2s = accel2Str.split(",");
                            if (gyro1Str != null){
                                gyro1s = gyro1Str.split(",");
                            }
                            if (gyro2Str!=null){
                                gyro2s = gyro2Str.split(",");
                            }

                            List<Integer> lenList = new LinkedList<>();
                            lenList.add(accel1s.length / 3);
                            lenList.add(accel2s.length / 3);
                            if (gyro1s !=null){
                                lenList.add(gyro1s.length / 3);
                            }
                            if (gyro2s !=null){
                                lenList.add(gyro2s.length / 3);
                            }

                            int len = Collections.min(lenList);
                            long time = new Date().getTime();
                            for (int i = 0; i < len; i++) {
                                timeTotal.add(time);
                                time += 10;
                            }// handling the time stamp

                            // Convert the fragment data to value
                            for (int i = 0; i < len; i++) {
                                List<Float> accel1 = new LinkedList<>();
                                List<Float> gyro1 = new LinkedList<>();
                                List<Float> accel2 = new LinkedList<>();
                                List<Float> gyro2 = new LinkedList<>();
                                for (int j = 0; j < 3; j++) {
                                    int buffer = Integer.parseInt(accel1s[i * 3 + j], 16);
                                    if (buffer > 32767)
                                        buffer -= 65536;
                                    accel1.add((float) (buffer * MPU_AccelResolution));
                                    accel1_Data=(float) (buffer * MPU_AccelResolution);
                                    if (gyro1s != null){
                                        buffer = Integer.parseInt(gyro1s[i * 3 + j], 16);
                                        if (buffer > 32767)
                                            buffer -= 65536;
                                        gyro1.add((float) (buffer * MPU_GyroResolution));
                                    }else{
                                        gyro1.add((float) (0));
                                    }



                                    buffer = Integer.parseInt(accel2s[i * 3 + j], 16);
                                    if (buffer > 32767)
                                        buffer -= 65536;
                                    accel2.add((float) (buffer * MPU_AccelResolution));
                                    accel2_Data=(float) (buffer * MPU_AccelResolution);
                                    if (gyro2s!=null){
                                        buffer = Integer.parseInt(gyro2s[i * 3 + j], 16);
                                        if (buffer > 32767)
                                            buffer -= 65536;
                                        gyro2.add((float) (buffer * MPU_GyroResolution));
                                    }else{
                                        gyro2.add((float)(0));

                                    }


                                }

                                ACCEL1Total.add(accel1);  // use attribute to store the data value
                                GYRO1Total.add(gyro1);
                                ACCEL2Total.add(accel2);
                                GYRO2Total.add(gyro2);
                                Number_ofcollected_data=Number_ofcollected_data+1;
                                if (Number_ofcollected_data%1000==0){

                                    System.out.println("The data collection is still working...");
                                    temp_Data=accel1_Data+" "+accel2_Data;
                                    System.out.println("We get the following ..."+temp_Data+" which is the "+Number_ofcollected_data+" th data.");
                                    if (gyro1s==null){
                                        System.out.println("gyro1s is not avaliable");
                                    }
                                    if (gyro2s==null){
                                        System.out.println("gyro2s is not avaliable");
                                    }
                                }
                            }
                        } else {
                            System.out.println(Msg);
                        }

                    } catch (Exception ex) {

                        if (ex.getMessage().indexOf("on a null object reference") != -1) {
                            errorCnt++;
                            if (errorCnt > 10) {
                                System.out.println("通信异常断开，请重新连接设备！");
                                isWhile = false;
                                break;
                            }
                        } else if (ex.getMessage().indexOf("你的主机中的软件中止了一个已建立的连接") != -1) {
                            System.out.println("设备已关闭连接，请重新开启设备热点后，重新运行此程序");
                            isWhile = false;
                        }
                        else
                            ex.printStackTrace();

                    }

                }
            }
        }.start(); // create a new thread to handle the server call back issue and also start it
    }


    public static void sendTcpMessage(String sendMsg) {
        //  We already create a socket at init
        new Thread() {
            @Override
            public void run() {
                try {
                    //2.获取输出流，向服务器端发送信息

                    PrintWriter pw = new PrintWriter(TCP_outputStream);// create a writer to send out the message based on the TCP_outputStream)
                    if (sendMsg.trim().equals("{\"func\":\"StartTask\"}")){
                        //System.out.println("Problemmatic command send out....!!!!");
                        pw.write("{\"func\":\"StartCollect\",\"isOpenGyro\":true,\"autoStopTime\":999999999999}");
                        //System.out.println("{\"func\":\"StartCollect\",\"isOpenGyro\":true,\"autoStopTime\":999999999999}"+" was send out to the data collection thread successfully");
                    }else{
                        pw.write(sendMsg);// send the text message
                        //System.out.println(sendMsg+" was send out to the data collection thread successfully");
                    }
                    pw.flush(); // force to output all the remaining text message from the memory
                    //System.out.println(sendMsg+" was send out to the data collection thread successfully");
//                    socket.shutdownOutput();//关闭输出流
                } catch (Exception e) {
                    e.printStackTrace(); // print the error message if error occur
                }
            }
        }.start();// create a thread to handle the output issue
    }
}
// https://www.youtube.com/watch?v=2Uk69nqv7As