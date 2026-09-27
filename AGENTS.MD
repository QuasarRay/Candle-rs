Project Goals:

1. Reimplement Candle in Rust and formally verify its source code Rust implementation to behave identically to the intended specification.

2. Create Supervision Infrastructure so for Human Engineers to be capable of independently verify what untrusted AI Agents implemented.

3. Use metaprogramming to the fullest potential.

4. Initially sacrifice performance optimization and code readability and idiomaticness in favor of reliability, faster development cycles, and preventing wasted credits/tokens

5. prefer code reuse over implementing from scratch. Reuse Boilerplate from the source codes of Verus and Kani to prevent tokens/credits from being wasted, and to accelerate development cycles.

6. prefer machine generated code over direct implementation.

7. use strong ISO Architecture Description Records to reduce token/credit of AI agents from being wasted, and make it possible for a solo human engineer to efficiently supervise a project scope larger than what is normally done by solo developers.

8. this AGENTS.md file should exist at every directory in the project repository.

9. Reuse mathematical specifications from Original Candle, while Rust implements those specifications. Also allow the scientific paper of Candle to guide you in the process of developing the Rust implementation. Treat the Original Candle's mathematical specifications as shared contract between Original Candle and Candle-rs. Both projects should understand the exact same specification files exactly in the same way and the same manner. therefore, the specifications share syntax as well as semantics.

10. use Kani to prevent mistakes from happening from the first time, prevent repeating a mistake that has been made, and as a means of human supervision. Also prevent progress from being lost by making stackable pull requests incrementally. Turn my github account into your workspace.

The Original Candle Github Repository: "https://github.com/CakeML/candle.git"

Target Project Repository: "https://github.com/QuasarRay/Candle-rs.git"