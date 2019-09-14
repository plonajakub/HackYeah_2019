package hack.yeah2019;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
@AllArgsConstructor
public class Article {
    private String url;
    private String target;
    private String guid;
    private Map<String, Double> tags;
}
