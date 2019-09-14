package hack.yeah2019;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;

@Data
@AllArgsConstructor
public class Article {
    private String url;
    private String target;
    private List<String> tags;
}
