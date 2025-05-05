# Changelog

<!--next-version-placeholder-->

## v0.4.0 (2024-10-05)

### Feature

* Draw_edges for simple layered graph ([`23845bd`](https://gitlab.com/gitabab/sugikey/-/commit/23845bdca2b166c85bcb07b87ae7230f9f7327aa))

### Fix

* Draw_config optional for backward_link_curve ([`4b07ea5`](https://gitlab.com/gitabab/sugikey/-/commit/4b07ea5da560135f4b2c2a7c165a9fb32a62a2c8))
* Iterative cycle edge removal fixed ([`268c3f7`](https://gitlab.com/gitabab/sugikey/-/commit/268c3f754bbf94b525f9815eb0cb2e7bc251f10e))
* Barycenter_heuristic_n_sweep min and max, not fixed ([`1fb62c7`](https://gitlab.com/gitabab/sugikey/-/commit/1fb62c7b6ba4375cfde56fcf74a68eacd18e44e6))

### Documentation

*  typing and docstring improvements ([`6c0c110`](https://gitlab.com/gitabab/sugikey/-/commit/6c0c110ec06b01366890bd5d7f300c4324328fd3))
* Get_layered_graph_layout (starting point) ([`1a4e16b`](https://gitlab.com/gitabab/sugikey/-/commit/1a4e16bbbb22640b268f6440301b084c4891f23c))

## v0.3.0 (2024-06-16)

### Feature

* Accept cycles ([`a0e38e3`](https://gitlab.com/gitabab/sugikey/-/commit/a0e38e396fe3c2242f317d147ea4d47bae2abd3c))

## v0.2.3 (2024-06-14)

### Fix

* Node imbalance with eps to avoid division by zero ([`5c9d7a8`](https://gitlab.com/gitabab/sugikey/-/commit/5c9d7a8d31c25b973976868cfc9b257a822c553c))

### Documentation

* Corrected docstring of cubic_spline_link ([`d5f963e`](https://gitlab.com/gitabab/sugikey/-/commit/d5f963ec6271339ef14c58304d54e18b6c221d24))

## v0.2.2 (2024-04-10)

### Fix

* Fixed two typing issues ([`28bd585`](https://gitlab.com/gitabab/sugikey/-/commit/28bd585036a2115a65c91ed184a2ec72d943ef67))

### Documentation

* Small readme update ([`f279056`](https://gitlab.com/gitabab/sugikey/-/commit/f2790562c5dd130bfd337f56da8972c3334bdb71))

## v0.2.1 (2024-04-10)

### Fix

* Fixed typing issues ([`53d35f5`](https://gitlab.com/gitabab/sugikey/-/commit/53d35f52972cf6820d39161fc5d768b4bf6c6419))

### Documentation

* Corrected keyerror in one notebook example ([`b78baed`](https://gitlab.com/gitabab/sugikey/-/commit/b78baed7133b31cea9259aab9066d781110c13ea))

## v0.2.0 (2024-03-01)

### Feature

* Beginning of edge coloring ([`f15cd57`](https://gitlab.com/gitabab/sugikey/-/commit/f15cd57222e6d170021466f0fe77e182b84ac8d1))

### Fix

* More parameters in DrawConfig, incl node_name_dy_drac and node_edge_kw" ([`2064dfa`](https://gitlab.com/gitabab/sugikey/-/commit/2064dfa8246d35ee90fb460fd8a4c9c316582ce7))
* Give node a color if all incoming and outcoming edges have the same color ([`8d08aad`](https://gitlab.com/gitabab/sugikey/-/commit/8d08aad6f4b995e19c58c59f644becdc6cb3f00c))
* Ha center default ([`d1acdc0`](https://gitlab.com/gitabab/sugikey/-/commit/d1acdc08e49e0ad8407c559f2acafea937fdad12))
* N_sweeps defined also for lp ([`f95756e`](https://gitlab.com/gitabab/sugikey/-/commit/f95756efdc8e118fe8f93e955ee178b4f832d6cc))
* 1st step towards coloring flows: adding attributes in df to dig conversion ([`f893063`](https://gitlab.com/gitabab/sugikey/-/commit/f8930632d2fa854a8c92859e4fbef91eab9ca27a))
* Barycenter_heuristic_n_sweeps in layoutConfig ([`a4305bd`](https://gitlab.com/gitabab/sugikey/-/commit/a4305bdd6d416491b885a2722b60f4f1c14d93cd))
* N_segments means n_segments+1 points, there should be at least 2 points ([`111151c`](https://gitlab.com/gitabab/sugikey/-/commit/111151c74784c4a1acb01c7479fc51cde15ee092))
* Better library error message in get_default_text_kwargs ([`8c36476`](https://gitlab.com/gitabab/sugikey/-/commit/8c36476b14c77e64be6c67e8cd0a3834aa01d2d3))

### Documentation

* Updated documentation with material-sphinx ([`5fa9b6f`](https://gitlab.com/gitabab/sugikey/-/commit/5fa9b6f6eed81a01285332c5da046d5586330166))
* Ref to why Sankey diagrams are so great ([`968d162`](https://gitlab.com/gitabab/sugikey/-/commit/968d16289da7a21173dec2edf42e71ec630728f8))
* System example CHP + HP + DH ([`bc71e26`](https://gitlab.com/gitabab/sugikey/-/commit/bc71e26e8eb6c56cc73c29d1c33973c8f10057da))
* Updated example notebook ([`3f02a63`](https://gitlab.com/gitabab/sugikey/-/commit/3f02a63ca1472e9794f8b540bf94bbc9c35930d8))
* Example data US 2020 ([`540b2aa`](https://gitlab.com/gitabab/sugikey/-/commit/540b2aa4a7a342c6b6903a0344daa7c65e6bc47e))
* Reference to the pip package ([`d3d76ca`](https://gitlab.com/gitabab/sugikey/-/commit/d3d76ca5b52573690664fbf61f806849aec788e6))
* Cleaned changelog ([`4e1740d`](https://gitlab.com/gitabab/sugikey/-/commit/4e1740d384c2815b7060fd37c36ab8d16583e425))

## v0.1.12 (2023-07-13)

### Fix

* Almost nothing ([`ebe585c`](https://gitlab.com/gitabab/sugikey/-/commit/ebe585cccb79d16ebb4d2c7db31d9e796d6225b7))

## v0.1.3 (2023-07-13)

### Fix

* Added missing type hints ([`e1bbe18`](https://gitlab.com/gitabab/sugikey/-/commit/e1bbe180d9fea259789c49434635a65cb8abb887))

## v0.1.2 (2023-07-13)

### Fix

* Unbalanced tuple unpacking ([`1d19d95`](https://gitlab.com/gitabab/sugikey/-/commit/1d19d959c953e1473b1632c3f1ebfcfb6de45dfd))

## v0.1.1 (2023-07-12)

### Fix

* Yet another try for sphinx pages ([`74765d6`](https://gitlab.com/gitabab/sugikey/-/commit/74765d6771443555a58a4a6a66d05e668d1ffd63))
* Mv _build/html public ([`df2cb66`](https://gitlab.com/gitabab/sugikey/-/commit/df2cb660fe35208f75176845af9ec45842701f3d))
* Artifact path docs/public ([`f0866ec`](https://gitlab.com/gitabab/sugikey/-/commit/f0866ec515ec00321bc266e80ec9a45e6f595f72))
* Call sphinx from the docs folder ([`86aeb29`](https://gitlab.com/gitabab/sugikey/-/commit/86aeb299142b3409ed5ecca4b88af2cb5174b518))
* Parameters of optimize_vertical_position_milp made better and more explicit ([`a502686`](https://gitlab.com/gitabab/sugikey/-/commit/a502686d381773f4bfeff935f0de0427f8f4eb55))

### Documentation

* Getting started md ([`78818bf`](https://gitlab.com/gitabab/sugikey/-/commit/78818bf11173d937f585517809f421adf909b62e))
* Sphinx gallery ([`f38608a`](https://gitlab.com/gitabab/sugikey/-/commit/f38608a60653c85da6de0bba4c069a6edc1aabcc))
* Readme on sphinx build ([`e926393`](https://gitlab.com/gitabab/sugikey/-/commit/e926393509cf3927e26cbb2c2d2e2758baf8313f))

## v0.1.0 (2023-04-04)
### Feature
* Starting to make some tooltips in bokeh ([`5add0ab`](https://gitlab.com/gitabab/sugikey/-/commit/5add0ab7dc696d258b9bb3396668996bfc6a0f0a))
* Beginning to plot with bokeh ([`544764d`](https://gitlab.com/gitabab/sugikey/-/commit/544764dc33defe7e5acf5b90d7c072c0eabb5e01))
* Base version, using pulp as dependency ([`6c552c0`](https://gitlab.com/gitabab/sugikey/-/commit/6c552c078f643f73c4792e4a51a50532de3aef8e))

### Documentation
* More complete readme ([`65e41db`](https://gitlab.com/gitabab/sugikey/-/commit/65e41db635488a401e309398076e4d0c77639ac5))
* Tree examples csv ([`ee6ad49`](https://gitlab.com/gitabab/sugikey/-/commit/ee6ad49b7695a321d123d9a890cce8ccbed63727))
* Iea example and more ([`d70c33d`](https://gitlab.com/gitabab/sugikey/-/commit/d70c33d4ff2c40d7abfd5c3e95e04a29bb7c437d))
* Additional example, siemese tree ([`e1ac166`](https://gitlab.com/gitabab/sugikey/-/commit/e1ac166a8962f353875016566a7a1defedf4d570))
* Very basic readme ([`8e8c793`](https://gitlab.com/gitabab/sugikey/-/commit/8e8c7936c960322d11393a034982ee27c34cfdcd))
* Example to start, tree with cross edge ([`bbb290d`](https://gitlab.com/gitabab/sugikey/-/commit/bbb290dcbf5549c75d0773cfe6ee59a69041e001))
