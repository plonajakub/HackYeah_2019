package hack.yeah2019;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import org.apache.http.client.fluent.Request;

import java.io.*;
import java.util.*;
import java.util.stream.Collectors;

public class Main {

    private static final ObjectMapper mapper = new ObjectMapper();
    private static final Random random = new Random();

    public static void main(String[] args) throws FileNotFoundException, JsonProcessingException {
        InputStream in;
        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream("links.txt")));
        PrintWriter writer = new PrintWriter(new FileOutputStream("result.txt"));
        List<Article> list = reader.lines().map(url -> {
            String response = null;
            try {
                System.out.println(url);
                response = Request.Get(url).execute().returnContent().asString();
                int begin = response.indexOf("{", response.indexOf("onetAds"));
                int end = response.indexOf("};", begin) + 1;
                String jsonInString = response.substring(begin, end);

                JsonNode node = mapper.readTree(jsonInString);
                JsonNode target = node.get("target");
                JsonNode guid = node.get("keyvalues").get("ci");
                ArrayNode keywords =  (ArrayNode) node.get("keywords");

                List<String> tags = mapper.convertValue(keywords, ArrayList.class);
                Map<String, Double> tagToWeight = new HashMap<>();
                tags.forEach(tag -> {
                    tagToWeight.put(tag, random.nextDouble() * 5);
                });

                return new Article(url, target.asText(), guid.asText(), tagToWeight);
            } catch (IOException e) {
                e.printStackTrace();
                throw new RuntimeException();
            }
        }).collect(Collectors.toList());
        Articles articles = new Articles(list);
        writer.println(mapper.writeValueAsString(articles));
        writer.flush();
        writer.close();
    }
}
