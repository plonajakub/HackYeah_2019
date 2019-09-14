package hack.yeah2019;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;

@Data
@AllArgsConstructor
public class Articles {
    private List<Article> articles;
}
