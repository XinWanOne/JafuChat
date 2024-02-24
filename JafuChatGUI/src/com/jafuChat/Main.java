package com.jafuChat;

import javax.swing.*;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.HyperlinkListener;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.io.*;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.prefs.BackingStoreException;
import java.util.prefs.Preferences;

public class Main extends JPanel {
    JEditorPane editor = new JEditorPane();
    JScrollPane scrollPane = new JScrollPane(editor);
    private OutputStream sendStream;

    JTextField input = new JTextField();
    JPanel buttonPanel = new JPanel();
    JPanel statusPanel = new JPanel();
    JPanel inputPanel = new JPanel(new BorderLayout());
    String dir = "E:\\docs\\";
    static String pythonExePath = "C:\\Users\\white\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";
    static String pythonSrcMain = "C:\\Users\\white\\Documents\\GitHub\\chatJafu\\build\\chatJafu\\main.py";
    static String documentsDir  = "";
    private static String LLM = "mistral";
    String headHtml = "</body></html>";
    String tailHtml = "</body></html>";
    String content = "";

    String cmd = "E:\\docs\\chatJafu\\venv\\Scripts\\python.exe E:\\docs\\chatJafu\\main.py";
    JLabel dirLabel;
    Thread thread;
    public Main() {
        this.dir = documentsDir;
        cmd =  pythonExePath+" "+pythonSrcMain+" -llm "+LLM;
        setLayout(new BorderLayout());
        add(scrollPane);
        add(buttonPanel,BorderLayout.WEST);
        add(inputPanel,BorderLayout.SOUTH);
        add(statusPanel,BorderLayout.NORTH);
        JButton dirButton = new JButton("Dir:");
        editor.setContentType("text/html");
        editor.addHyperlinkListener(new HyperlinkListener() {
            public void hyperlinkUpdate(HyperlinkEvent e) {
                if(e.getEventType() == HyperlinkEvent.EventType.ACTIVATED) {
                    if(Desktop.isDesktopSupported()) {
                        try {
                            Desktop.getDesktop().browse(e.getURL().toURI());
                        } catch (IOException | URISyntaxException ex) {
                            throw new RuntimeException(ex);
                        }
                    }
                }
            }
        });


        dirButton.addActionListener((e)->changDir(e));
        dirLabel = new JLabel(dir);
        statusPanel.add(dirButton);
        statusPanel.add(dirLabel);
        statusPanel.add(new JLabel("  CMD:"+cmd));
        inputPanel.add(new JLabel("  Question: "),BorderLayout.WEST);
        inputPanel.add(input);
        editor.setEditable(false);
        buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));
        File[]d = new File(dir).listFiles();
        buttonPanel.add(new JLabel("Directories"));
        if (d != null)
        for (int i = 0; i < d.length; i++) {
            File file = d[i];
            if (!file.isDirectory()){
                continue;
            }
            if ("chatJafu".equalsIgnoreCase(file.getName())){
                continue;
            }
            buttonPanel.setBackground(Color.lightGray);
            JButton button = new JButton(file.getName());
            button.addActionListener((a)->{
                sendComand("quit");
                editor.setText("");
                backgroundRun(cmd, file.getAbsolutePath());
            });
            buttonPanel.add(button);
        }

        editor.setFont(editor.getFont().deriveFont(24f));
        input.setFont(editor.getFont().deriveFont(24f));
        if (d != null) {
            backgroundRun(cmd, d[0].getAbsolutePath());
        }
        input.addActionListener(new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                sendComand(input.getText());
            }
        });
    }

    private void changDir(ActionEvent e) {
        JFileChooser chooser = new JFileChooser(dir);
        chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        int ans = chooser.showOpenDialog(this);
        if (ans == JFileChooser.APPROVE_OPTION) {
           File f = chooser.getSelectedFile();
            System.out.println(" "+f.getAbsolutePath());
            dir = f.getAbsolutePath();
            dirLabel.setText(dir);
            ourLayoutPrefs.put("dir",dir);
        }
    }

    void backgroundRun(String cmd,String dir){
        thread  = new Thread() {
            @Override
            public void run() {
                runCmd(cmd+" " +dir);
            }
        };
        thread.start();
    }

    void sendComand(String str) {
        addLine(str);
        input.setText("");
        try {

            sendStream.write((str+"\n").getBytes());

            sendStream.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

       static   Map<Character, String> replacements = new HashMap<>();

    static {
        replacements.put('&', "&amp;");
        replacements.put('>', "&gt;");
        replacements.put('<', "&lt;");
        replacements.put('\'', "&apos;");
        replacements.put('"', "&quot;");
    }

    private String htmlEscape(String input) {
        if (input.matches("> .* pg: .*")){
            return  "<a href=\"file:///"+ input.replaceAll("> (.*) pg: (.*)","$1#page=$2\">$1($2)</a>");
        }
        StringBuilder sb = new StringBuilder(input.length());
        for (char c : input.toCharArray()) {
            if (replacements.containsKey(c)) {
                sb.append(replacements.get(c));
            } else {
                sb.append(c);
            }

        }
        return sb.toString();
    }
    public void addLine(final  String str) {
        SwingUtilities.invokeLater(()->{

            String text =  htmlEscape(str);
            System.out.println(text);
            while (text.length() > 80) {
                int cut = text.lastIndexOf(" ",80);
                if (cut <= 65) {
                    break;
                }
                String bit = text.substring(0,cut);
                content += "<br>"+bit;
                System.out.println(".");
                text =  text.substring(cut);
            }

            content += "<br>"+ text;

            editor.setText(headHtml+content+tailHtml );

            JScrollBar vertical = scrollPane.getVerticalScrollBar();
            vertical.setValue( vertical.getMaximum() );
        });
    }

    private  void runCmd(String cmd) {

        try {
            // Run "netsh" Windows command
            System.out.println("running "+ cmd);
            Process process = Runtime.getRuntime().exec(cmd);

            // Get input streams
            BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));
            BufferedReader stdError = new BufferedReader(new InputStreamReader(process.getErrorStream()));

            // Read command standard output
            String s;
            sendStream = process.getOutputStream();
            while ((s = stdInput.readLine()) != null) {
                addLine(s);
            }

            // Read command errors
            Thread t =  new Thread() {
                @Override
                public void run() {
                    String s;

                        try {
                            while ((s = stdError.readLine()) != null) {
                                System.err.println(s);
                            }

                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        }
                }
            };
            t.start();

        } catch (Exception e) {
            e.printStackTrace(System.err);
        }
    }
    private static final String DEFAULT_LAYOUT_NAME = "default";

    private static HashMap<String, JFrame> ounKnownFrames = new HashMap<>();
    //////////////////////////////////////////////////////////////////////
    private static Preferences ourLayoutPrefs = Preferences.userNodeForPackage(Main.class);
    public static Rectangle getLastLayout(Rectangle rec) {

            rec.x = ourLayoutPrefs.getInt( "base_x", rec.x);
            rec.y = ourLayoutPrefs.getInt(  "base_y", rec.y);
            rec.width = ourLayoutPrefs.getInt(  "base_width", rec.width);
            rec.height = ourLayoutPrefs.getInt(  "base_height", rec.height);
            return rec;
        }

    public static void rememberPosition(JFrame frame, Rectangle defaultPos) {
        Rectangle pos;

        if (defaultPos != null) {
            pos = defaultPos;
        } else {
            pos = new Rectangle(100, 100, 1200, 800);
        }
        String name = frame.getContentPane().getClass().getSimpleName();


         getLastLayout(pos);
        frame.setBounds(pos);
        frame.addComponentListener(new ComponentAdapter() {
            @Override
            public void componentResized(ComponentEvent e) {
                resize();
            }

            public void componentMoved(ComponentEvent evt) {
                resize();
            }

            void resize() {
                 var pref=   ourLayoutPrefs;
                 var rec =  frame.getBounds();
                pref.putInt("base_x", rec.x);
                pref.putInt("base_y", rec.y);
                pref.putInt("base_width", rec.width);
                pref.putInt("base_height", rec.height);
                try {
                    pref.flush();
                } catch (BackingStoreException e) {
                    throw new RuntimeException(e);
                }
            }
        });
    }


    ////////////////////////////////////////////////////////////////////


    public static void main(String[] args) throws IOException {
        JFrame f = new JFrame("ChatJafu");
        rememberPosition(f,null);
        if (args.length < 1) {
            System.err.println("set config on command line ");
            System.exit(1);
        }

        Properties p = new Properties();
        p.load(new FileReader(args[0]));
        Main.pythonExePath = p.getProperty("python");
        Main.pythonSrcMain = p.getProperty("main");
        Main.documentsDir = p.getProperty("documents");
        Main.LLM = p.getProperty("llm", Main.LLM);
        System.out.println("model="+Main.LLM);

        URL iconURL = Main.class.getResource("logo.png");
        System.out.println(iconURL);
// iconURL is null when not found
        ImageIcon icon = new ImageIcon(iconURL);

        f.setIconImage(icon.getImage());
        f.setContentPane(new Main());
        f.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);

        f.setVisible(true);
    }
}
